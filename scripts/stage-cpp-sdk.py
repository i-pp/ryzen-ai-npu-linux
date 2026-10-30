#!/usr/bin/env python3
"""Stage a licensed C++ subset; no Python install, ELF patch, or vendor execution."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('stage_xrt', Path(__file__).with_name('stage-xrt.py'))
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)
HEADERS = {'onnxruntime_c_api.h': 'c4ed26d7bbc7b649c1c38622424d88dfb1a28e3d3594c5f1456cf458814e8381',
           'onnxruntime_ep_c_api.h': 'f65ac849718cabe3ff4902698dd2de643c3b3dbe0010242b2b0407548e7ee00c'}
MODEL_SHA256 = '7a78c7e85bac3a0681e3d2f77e69093a761e1c8f62f7fc65ff5ce3e1b82c5ba3'
PEANO_SIZE = 186631968


def load_baseline(path):
    raw = path.read_bytes()
    baseline = json.loads(raw)
    if not isinstance(baseline, dict) or baseline.get('schema_version') != 1:
        raise ValueError('unsupported baseline manifest')
    gaps = []
    identity = baseline.get('identity_kind')
    ident = baseline.get('baseline_id')
    if not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9][a-z0-9.-]{2,95}', ident):
        gaps.append('a concrete baseline_id is required')
    if identity not in ('historical-restore', 'new-acquisition'):
        gaps.append('identity_kind must distinguish historical-restore and new-acquisition')
    if identity == 'new-acquisition' and (not isinstance(ident, str) or not ident.startswith('new-')):
        gaps.append('new acquisitions require a unique new-... baseline_id')
    if baseline.get('review_status') != 'reviewed':
        gaps.append('manifest review_status is not reviewed')
    expected_names = {'onnxruntime': 'onnxruntime.tar.gz',
                      'sdk_peano': 'llvm_aie-1.8.0-py3-none-linux_x86_64.whl',
                      'quicktest': 'quicktest.tar.gz'}
    artifacts = baseline.get('artifacts', {})
    if not isinstance(artifacts, dict):
        raise ValueError('baseline artifacts must be an object')
    inputs = {}
    for key, name in expected_names.items():
        item = artifacts.get(key, {})
        if not isinstance(item, dict) or item.get('filename') != name:
            raise ValueError('unexpected baseline artifact filename: ' + key)
        value = item.get('sha256')
        if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
            gaps.append('full reviewed archive hash missing: ' + key)
        inputs[name] = value
        if not isinstance(item.get('source_url'), str) or not item['source_url'].startswith('https://'):
            gaps.append('acquisition source missing: ' + key)
        if identity == 'historical-restore' and not item.get('distribution_member'):
            gaps.append('historical outer distribution member path missing: ' + key)
    if artifacts['onnxruntime'].get('payload_root') != 'onnxruntime' or \
            artifacts['sdk_peano'].get('payload_member') != 'lnx64.o/tools/peano/lib/libpeano-lib.so.21.0git' or \
            artifacts['sdk_peano'].get('payload_size_bytes') != PEANO_SIZE or \
            artifacts['quicktest'].get('payload_member') != 'quicktest/test_model.onnx':
        raise ValueError('baseline member contract differs from this C++ subset helper')
    if baseline.get('headers') != HEADERS or baseline.get('model_sha256') != MODEL_SHA256:
        raise ValueError('baseline header/model pins differ from the recorded probe contract')
    if identity == 'historical-restore':
        distribution = baseline.get('distribution', {})
        if not isinstance(distribution, dict) or not re.fullmatch(r'[0-9a-f]{64}', str(distribution.get('sha256', ''))):
            gaps.append('historical complete distribution hash missing')
        if not baseline.get('historical_identity_evidence'):
            gaps.append('historical identity source review missing')
    elif identity == 'new-acquisition' and not baseline.get('acquisition_notes'):
        gaps.append('new acquisition evidence/notes missing')
    return baseline, inputs, gaps, hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archives', required=True, type=Path, help='manually obtained SDK 1.8.0 extracted distribution directory')
    p.add_argument('--headers', required=True, type=Path, help='official ORT v1.27.0 headers, separately acquired')
    p.add_argument('--baseline', type=Path, default=ROOT / 'artifacts/baselines/historical-cpp-sdk-1.8.0.json',
                   help='reviewed input manifest; unknown historical pins block apply, new acquisitions need their own ID')
    p.add_argument('--destination', type=Path, default=ROOT / '.private-work/cpp-sdk')
    p.add_argument('--apply', action='store_true')
    p.add_argument('--acknowledge-sdk-license', action='store_true', help='operator confirms their authorized local use; no license is granted by this repository')
    a = p.parse_args()
    dest = st.destination(a.destination)
    baseline, inputs, gaps, manifest_sha = load_baseline(a.baseline)
    identity = {'baseline_id': baseline.get('baseline_id'), 'identity_kind': baseline.get('identity_kind'),
                'manifest_sha256': manifest_sha,
                'historical_archive_identity_claimed': baseline.get('identity_kind') == 'historical-restore' and not gaps}
    if not a.apply:
        print(json.dumps({'status': 'PLAN', 'inputs': list(inputs), 'destination': str(dest.relative_to(ROOT)),
                          'archives_hashed': False, 'effect': 'extract C++ runtime, pinned model, SDK Peano and matched headers only',
                          'python_environment_created': False, 'baseline': identity, 'apply_blockers': gaps}))
        return
    if gaps:
        raise ValueError('baseline cannot be applied: ' + '; '.join(gaps))
    if not a.acknowledge_sdk_license:
        p.error('--apply requires explicit --acknowledge-sdk-license after independent review of AMD terms')
    for name, expected in inputs.items():
        if not re.fullmatch(r'[0-9a-f]{64}', expected):
            p.error('a real lowercase SHA-256 is required for ' + name)
        if st.digest(a.archives / name) != expected:
            p.error('archive SHA-256 mismatch: ' + name)
    for name, expected in HEADERS.items():
        if st.digest(a.headers / name) != expected:
            p.error('ORT v1.27.0 header mismatch: ' + name)
    fingerprint = {'archives': inputs, 'headers': HEADERS, 'baseline': identity}
    receipt = dest / 'sdk-stage-receipt.json'
    if dest.exists():
        if receipt.is_file():
            previous = json.loads(receipt.read_text())
            current = st.tree_hashes(dest / 'cpp-test')
            # These are the only extra files deliberately created later by
            # build-probe.py. Extra SDK libraries still count as drift.
            current = {k: v for k, v in current.items() if k not in ('inference-probe', 'probe-build.json')}
            if previous.get('inputs') == fingerprint and previous.get('files') == current:
                print(json.dumps({'status': 'PASS', 'action': 'already staged; complete subset hashes verified'}))
                return
        raise ValueError('existing destination/receipt differs; preserved without changes')
    dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lockdir = dest.with_name(dest.name + '.lock')
    lockdir.mkdir(mode=0o700)
    tmp = Path(tempfile.mkdtemp(prefix=dest.name + '.partial-', dir=dest.parent))
    try:
        cpp = tmp / 'cpp-test'
        sdkdir = cpp / 'sdk'
        sdkdir.mkdir(parents=True)
        total = 0
        with tarfile.open(a.archives / 'onnxruntime.tar.gz', 'r|gz') as archive:
            for member in archive:
                name = member.name.removeprefix('./')
                if name != 'onnxruntime' and not name.startswith('onnxruntime/'):
                    raise ValueError('unexpected C++ SDK archive root')
                total += member.size
                if total > 8 * 1024**3 or member.size > 512 * 1024**2:
                    raise ValueError('C++ archive exceeds documented extraction cap')
                archive.extract(member, path=sdkdir, filter='data')
        modeldir = cpp / 'samples/quicktest'
        modeldir.mkdir(parents=True)
        with tarfile.open(a.archives / 'quicktest.tar.gz', 'r:gz') as archive:
            member = archive.getmember('quicktest/test_model.onnx')
            if not member.isfile() or member.size > 64 * 1024**2:
                raise ValueError('unexpected model member')
            with archive.extractfile(member) as src, (modeldir / 'test_model.onnx').open('xb') as out:
                shutil.copyfileobj(src, out, 1024 * 1024)
        if st.digest(modeldir / 'test_model.onnx') != MODEL_SHA256:
            raise ValueError('model bytes do not match the historical model')
        peano = cpp / 'peano'
        peano.mkdir()
        member_name = 'lnx64.o/tools/peano/lib/libpeano-lib.so.21.0git'
        with zipfile.ZipFile(a.archives / 'llvm_aie-1.8.0-py3-none-linux_x86_64.whl') as archive:
            info = archive.getinfo(member_name)
            if info.file_size != PEANO_SIZE:
                raise ValueError('unexpected SDK Peano size')
            with archive.open(info) as src, (peano / 'libpeano-lib.so.21.0git').open('xb') as out:
                shutil.copyfileobj(src, out, 1024 * 1024)
        (peano / 'libpeano-lib.so').symlink_to('libpeano-lib.so.21.0git')
        (cpp / 'include').mkdir()
        for name in HEADERS:
            shutil.copyfile(a.headers / name, cpp / 'include' / name)
        (tmp / 'sdk-stage-receipt.json').write_text(json.dumps({'inputs': fingerprint, 'files': st.tree_hashes(cpp)}, indent=2))
        if dest.exists():
            raise ValueError('destination appeared during staging; partial preserved')
        os.rename(tmp, dest)
        print(json.dumps({'status': 'PASS', 'action': 'staged isolated C++ subset', 'vendor_runtime_executed': False}))
    finally:
        lockdir.rmdir()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, tarfile.TarError, zipfile.BadZipFile, KeyError) as e:
        print(json.dumps({'status': 'FAIL', 'detail': str(e), 'recovery': 'input/old destination preserved; inspect partial staging manually'}))
        raise SystemExit(1)
