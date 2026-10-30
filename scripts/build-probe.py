#!/usr/bin/env python3
"""Plan/build the new probe in .private-work, preserving all existing outputs."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOL_ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}
HEADERS = {'onnxruntime_c_api.h': 'c4ed26d7bbc7b649c1c38622424d88dfb1a28e3d3594c5f1456cf458814e8381',
           'onnxruntime_ep_c_api.h': 'f65ac849718cabe3ff4902698dd2de643c3b3dbe0010242b2b0407548e7ee00c'}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def leaf_info(parent_fd, name):
    try:
        info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('output is a symlink or unexpected existing object: ' + name)
    return info


def read_leaf(parent_fd, name):
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
    with os.fdopen(fd, 'rb') as stream:
        return stream.read()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk-root', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    a = parser.parse_args(argv)
    sdk = a.sdk_root.resolve()
    if not a.apply:
        print(json.dumps({'status': 'PLAN', 'effect': 'compile newly authored probe only',
                          'compiler_selection': 'resolve g++ once from /usr/bin:/bin; same absolute file/environment for version and build',
                          'flags': '-std=c++17 -O2 -Wall -Wextra -I<SDK>/cpp-test/include -L<SDK>/cpp-test/sdk/onnxruntime/lib -Wl,-rpath,$ORIGIN/sdk/onnxruntime/lib -lonnxruntime',
                          'output': '<SDK>/cpp-test/inference-probe', 'execution': False}))
        return
    base = ROOT / '.private-work'
    if base.is_symlink() or not sdk.is_relative_to(base) or sdk == base:
        raise ValueError('--apply requires an isolated SDK root inside this repository/.private-work')
    cpp_path = sdk / 'cpp-test'
    if cpp_path.is_symlink():
        raise ValueError('output parent must not be a symlink')
    cpp = cpp_path.resolve(strict=True)
    if not cpp.is_relative_to(base) or not cpp.is_dir():
        raise ValueError('output parent escapes .private-work or is not a directory')
    source = ROOT / 'src/inference-probe.cpp'
    inputs = [source, ROOT / 'src/exclusive-output.hpp',
              *[cpp / 'include' / name for name in HEADERS],
              cpp / 'sdk/onnxruntime/lib/libonnxruntime.so']
    if any(not path.is_file() for path in inputs):
        raise ValueError('source/header/runtime input missing')
    if any(not path.resolve().is_relative_to(base) for path in inputs[2:]):
        raise ValueError('SDK inputs must not link to a preserved environment')
    if any(sha(cpp / 'include' / name) != expected for name, expected in HEADERS.items()):
        raise ValueError('headers do not match the recorded official ORT v1.27.0 pair')
    parent_fd = os.open(cpp, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    parent_identity = os.fstat(parent_fd)
    lock_created = False
    app_name, receipt_name = 'inference-probe', 'probe-build.json'
    lock_name = '.probe-build.lock'
    try:
        try:
            os.mkdir(lock_name, mode=0o700, dir_fd=parent_fd)
            lock_created = True
        except FileExistsError as e:
            raise ValueError('build lock exists; no compiler started') from e
        app_info = leaf_info(parent_fd, app_name)
        receipt_info = leaf_info(parent_fd, receipt_name)
        if bool(app_info) != bool(receipt_info):
            raise ValueError('unpaired existing build output; preserved without changes')
        compiler_name = shutil.which('g++', path=TOOL_ENV['PATH'])
        if compiler_name is None:
            raise ValueError('g++ is absent from the fixed tool path')
        compiler = Path(compiler_name).resolve(strict=True)
        flags = ['-std=c++17', '-O2', '-Wall', '-Wextra', '-I', str(cpp / 'include'), str(source),
                 '-L', str(cpp / 'sdk/onnxruntime/lib'), '-Wl,-rpath,$ORIGIN/sdk/onnxruntime/lib', '-lonnxruntime']
        fingerprint = {'schema_version': 2, 'input_sha256': [sha(path) for path in inputs],
                       'compiler_realpath': str(compiler), 'compiler_sha256': sha(compiler),
                       'compiler_environment': TOOL_ENV, 'flags': flags}
        if app_info:
            old = json.loads(read_leaf(parent_fd, receipt_name))
            if isinstance(old, dict) and old.get('fingerprint') == fingerprint and \
                    old.get('application_sha256') == hashlib.sha256(read_leaf(parent_fd, app_name)).hexdigest():
                print(json.dumps({'status': 'PASS', 'action': 'already built; identities verified', 'runtime_tested': False}))
                return
            raise ValueError('existing build differs or lacks an owned receipt; preserved without changes')
        version = subprocess.run([str(compiler), '--version'], capture_output=True, text=True,
                                 check=True, timeout=10, env=TOOL_ENV).stdout.splitlines()[0]
        with tempfile.TemporaryDirectory(prefix='.probe-build-', dir=cpp) as temporary:
            temp = Path(temporary)
            temp_app = temp / app_name
            command = [str(compiler), *flags, '-o', str(temp_app)]
            subprocess.run(command, check=True, timeout=60, env=TOOL_ENV, cwd=temp)
            if not temp_app.is_file() or temp_app.is_symlink():
                raise ValueError('compiler did not create a regular private output')
            temp_receipt = temp / receipt_name
            record = {'fingerprint': fingerprint, 'compiler_version': version,
                      'build_argv': command, 'application_sha256': sha(temp_app),
                      'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      'runtime_tested': False}
            with temp_receipt.open('x') as stream:
                json.dump(record, stream, indent=2)
            if cpp_path.is_symlink() or cpp_path.resolve() != cpp:
                raise ValueError('output parent changed during build')
            current_parent = cpp_path.stat(follow_symlinks=False)
            if (current_parent.st_dev, current_parent.st_ino) != (parent_identity.st_dev, parent_identity.st_ino):
                raise ValueError('output parent inode changed during build')
            if leaf_info(parent_fd, app_name) or leaf_info(parent_fd, receipt_name):
                raise ValueError('output appeared during build; preserved without changes')
            published_app = False
            try:
                # Hard links publish with no replacement, including dangling
                # symlinks created after the initial check.
                os.link(temp_app, app_name, dst_dir_fd=parent_fd, follow_symlinks=False)
                published_app = True
                os.link(temp_receipt, receipt_name, dst_dir_fd=parent_fd, follow_symlinks=False)
            except OSError:
                if published_app:
                    current = os.stat(app_name, dir_fd=parent_fd, follow_symlinks=False)
                    original = temp_app.stat()
                    if (current.st_dev, current.st_ino) == (original.st_dev, original.st_ino):
                        os.unlink(app_name, dir_fd=parent_fd)
                raise
        print(json.dumps({'status': 'PASS', 'action': 'built and published new probe without replacement', 'runtime_tested': False}))
    finally:
        if lock_created:
            os.rmdir(lock_name, dir_fd=parent_fd)
        os.close(parent_fd)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        print(json.dumps({'status': 'FAIL', 'detail': str(e), 'runtime_tested': False}))
        raise SystemExit(1)
