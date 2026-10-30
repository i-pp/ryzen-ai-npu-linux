#!/usr/bin/env python3
"""Plan or stage pinned XRT user-space files inside .private-work. No install."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.private-work'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def destination(path):
    if BASE.is_symlink():
        raise ValueError('.private-work must not be a symlink')
    path = path.resolve()
    if not path.is_relative_to(BASE) or path == BASE:
        raise ValueError('destination must be a child of this repository/.private-work')
    return path


def tree_hashes(root):
    out = {}
    for p in sorted(root.rglob('*')):
        if p.is_file() or p.is_symlink():
            if not p.resolve().is_relative_to(root):
                raise ValueError('staged symlink escapes destination')
            out[str(p.relative_to(root))] = digest(p)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packages', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=BASE / 'xrt-2.25.37')
    parser.add_argument('--apply', action='store_true', help='opt in to local extraction; never invokes package maintainer scripts')
    a = parser.parse_args()
    dest = destination(a.destination)
    lock = json.loads((ROOT / 'artifacts/xrt-packages.json').read_text())
    package_dir = a.packages.resolve()
    if not a.apply:
        print(json.dumps({'status': 'PLAN', 'packages': [x['name'] for x in lock['packages']],
                          'destination': str(dest.relative_to(ROOT)),
                          'input_hashes_verified': False,
                          'effect': 'extract only opt/xilinx/xrt user-space payload; no sudo/dpkg installation/device use'}))
        return
    for item in lock['packages']:
        if digest(package_dir / item['name']) != item['sha256']:
            raise ValueError('package SHA-256 mismatch: ' + item['name'])
    receipt = dest / 'stage-receipt.json'
    if dest.exists():
        if not receipt.is_file():
            raise ValueError('destination exists without receipt; preserved without changes')
        previous = json.loads(receipt.read_text())
        if previous['packages'] != lock['packages'] or previous['files'] != tree_hashes(dest / 'opt'):
            raise ValueError('staged content drift; preserved without changes')
        print(json.dumps({'status': 'PASS', 'action': 'already staged, hashes verified'}))
        return
    BASE.mkdir(mode=0o700, exist_ok=True)
    dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lockdir = dest.with_name(dest.name + '.lock')
    lockdir.mkdir(mode=0o700)  # Atomic single-writer guard; do not remove another run's lock.
    tmp = Path(tempfile.mkdtemp(prefix=dest.name + '.partial-', dir=dest.parent))
    try:
        total = 0
        for item in lock['packages']:
            proc = subprocess.Popen(['dpkg-deb', '--fsys-tarfile', str(package_dir / item['name'])],
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
            try:
                with tarfile.open(fileobj=proc.stdout, mode='r|') as archive:
                    for member in archive:
                        name = member.name.removeprefix('./')
                        if not name.startswith('opt/xilinx/xrt/'):
                            continue
                        if '..' in Path(name).parts or member.isdev() or member.isfifo():
                            raise ValueError('unsafe archive member')
                        total += member.size
                        if total > 512 * 1024 * 1024:
                            raise ValueError('uncompressed payload exceeds 512 MiB cap')
                        archive.extract(member, path=tmp, filter='data')
                if proc.wait(timeout=30):
                    raise ValueError('dpkg-deb payload decompression failed')
            finally:
                proc.stdout.close()
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=5)
        for name in ['libxrt_coreutil.so.2', 'libxrt_core.so.2', 'libxrt_driver_xdna.so.2']:
            if not (tmp / 'opt/xilinx/xrt/lib' / name).is_file():
                raise ValueError('required runtime library missing: ' + name)
        v = json.loads((tmp / 'opt/xilinx/xrt/version.json').read_text())
        if '2.25.37' not in json.dumps(v):
            raise ValueError('unexpected XRT version metadata')
        (tmp / 'stage-receipt.json').write_text(json.dumps({'packages': lock['packages'], 'files': tree_hashes(tmp / 'opt')}, indent=2))
        if dest.exists():
            raise ValueError('destination appeared during extraction; staged partial preserved')
        os.rename(tmp, dest)
        print(json.dumps({'status': 'PASS', 'action': 'staged user-space payload', 'destination': str(dest.relative_to(ROOT))}))
    finally:
        lockdir.rmdir()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, tarfile.TarError, subprocess.TimeoutExpired) as e:
        print(json.dumps({'status': 'FAIL', 'detail': str(e), 'recovery': 'inputs/destination preserved; inspect any .partial directory manually'}))
        raise SystemExit(1)
