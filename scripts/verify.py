#!/usr/bin/env python3
"""Read-only checks and offline evidence evaluation. Never imports vendor modules."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

# -I disables implicit script-directory imports; load our own sibling explicitly.
spec = importlib.util.spec_from_file_location('evidence_tools', Path(__file__).with_name('evidence_tools.py'))
et = importlib.util.module_from_spec(spec)
spec.loader.exec_module(et)
ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['environment', 'mlir-aie', 'iron', 'inference', 'model', 'compare'])
    p.add_argument('--sdk-root', type=Path)
    p.add_argument('--mlir-root', type=Path)
    p.add_argument('--xrt-root', type=Path)
    p.add_argument('--log', type=Path)
    p.add_argument('--stderr-log', type=Path)
    p.add_argument('--run-result', type=Path)
    p.add_argument('--model', type=Path)
    p.add_argument('--reference', type=Path)
    p.add_argument('--candidate', type=Path)
    p.add_argument('--atol', type=float)
    p.add_argument('--rtol', type=float)
    a = p.parse_args()
    checks = []

    def add(key, status, detail):
        checks.append({'id': key, 'status': status, 'detail': detail})

    def file_check(key, path):
        if path is None:
            add(key, 'SKIP', 'path not supplied')
        else:
            add(key, 'PASS' if path.is_file() else 'FAIL', 'file present' if path.is_file() else 'file missing')

    if a.mode == 'environment':
        try:
            s = et.command(['lspci', '-nnk', '-d', '1022:17f0'])
            add('pci', 'PASS' if '1022:17f0' in s else 'FAIL', 'expected PCI function detected' if '1022:17f0' in s else 'expected PCI function not reported')
            add('driver-binding', 'PASS' if 'Kernel driver in use: amdxdna' in s else 'SKIP', 'lspci binding inspected; absent binding requires host investigation')
        except (OSError, ValueError) as e:
            add('pci', 'SKIP', str(e))
        dev = Path('/dev/accel/accel0')
        add('device-access', 'SKIP' if not dev.exists() else
            ('PASS' if os.access(dev, os.R_OK | os.W_OK) else 'FAIL'),
            'node unavailable to this namespace' if not dev.exists() else 'effective read/write access check, no device open')
        soft, hard = resource.getrlimit(resource.RLIMIT_MEMLOCK)
        add('process-memlock', 'PASS' if (soft == resource.RLIM_INFINITY or soft >= 1073741824) else 'FAIL',
            {'soft_bytes': soft, 'hard_bytes': hard, 'criterion': 'snapshot target 1 GiB; not a universal minimum'})
        for key, argv in [('system-xrt', ['dpkg-query', '-W', '-f=${Version}', 'libxrt2']),
                          ('driver-module', ['modinfo', '-F', 'filename', 'amdxdna'])]:
            try:
                s = et.command(argv).strip()
                add(key, 'PASS' if s else 'FAIL', s)
            except (OSError, ValueError) as e:
                add(key, 'SKIP', str(e))
        file_check('firmware-file', Path('/lib/firmware/amdnpu/17f0_11/npu_7.sbin.zst'))
        add('loaded-firmware-version', 'SKIP', 'on-disk firmware is not proof of loaded firmware version; use saved boot journal')
        add('systemd-effective-limit', 'SKIP', 'no service bus probe; capture from authorized host shell separately')
    elif a.mode == 'mlir-aie':
        if a.mlir_root is None:
            add('mlir-root', 'SKIP', 'path not supplied')
        else:
            try:
                rev = et.command(['git', '-C', str(a.mlir_root), 'rev-parse', 'HEAD']).strip()
                add('mlir-revision', 'PASS' if rev == 'e28f6dc7e52fbb7b43f94b3693083c3f01a2387c' else 'FAIL', rev)
                dirty = et.command(['git', '-C', str(a.mlir_root), 'status', '--porcelain', '--untracked-files=no'])
                add('mlir-local-changes', 'PASS', {'changed_tracked_files': len(dirty.splitlines()), 'meaning': 'inventory only; local edits must be retained and reviewed'})
            except (OSError, ValueError) as e:
                add('mlir-revision', 'SKIP', str(e))
            cfg = a.mlir_root / 'ironenv/pyvenv.cfg'
            file_check('iron-python-config', cfg)
            if cfg.is_file():
                version = next((l.split('=', 1)[1].strip() for l in cfg.read_text().splitlines() if l.startswith('version =')), '')
                add('iron-python-version', 'PASS' if version == '3.14.4' else 'FAIL', version)
            site = a.mlir_root / 'ironenv/lib/python3.14/site-packages'
            for name, version in [('mlir_aie', '1.4.5.dev113+ge28f6dc'), ('llvm_aie', '22.0.0.2026102001+4f5df13d'), ('numpy', '2.5.4')]:
                file_check(name + '-metadata', site / f'{name}-{version}.dist-info/METADATA')
            add('mlir-import-compatibility', 'SKIP', 'distribution files alone do not prove native import/platform compatibility')
    elif a.mode in ('iron', 'inference'):
        if a.log is None:
            add('saved-log', 'SKIP', 'no log supplied; device execution is never automatic')
        else:
            if a.log.stat().st_size > 16 * 1024 * 1024:
                raise ValueError('log exceeds 16 MiB evaluation cap')
            text = a.log.read_text(errors='replace')
            if a.stderr_log is not None:
                if a.stderr_log.stat().st_size > 16 * 1024 * 1024:
                    raise ValueError('stderr log exceeds 16 MiB evaluation cap')
                text += '\n' + a.stderr_log.read_text(errors='replace')
            result = et.iron_log(text) if a.mode == 'iron' else et.inference_log(text)
            ok = result['pass_marker'] and not result['failure_marker'] if a.mode == 'iron' else result['api_success']
            add('saved-log', 'PASS' if ok else 'FAIL', {'sha256': et.sha256(a.log), 'analysis': result})
            if a.mode == 'inference':
                add('reported-npu-execution', 'PASS' if result['reported_npu_execution'] else 'SKIP', 'runtime log attribution, not an independent hardware trace')
        if a.run_result is not None:
            if a.run_result.stat().st_size > 1024 * 1024:
                raise ValueError('run metadata exceeds 1 MiB evaluation cap')
            recorded = json.loads(a.run_result.read_text())
            if not isinstance(recorded, dict):
                raise ValueError('run metadata must be a JSON object')
            rc = recorded.get('exit_code')
            add('recorded-process-exit', 'PASS' if type(rc) is int and rc == 0 else 'FAIL',
                {'exit_code': rc, 'scope': 'supplied run metadata; this verifier never starts a process'})
        else:
            add('recorded-process-exit', 'SKIP', 'exit status is not present in a bare historical log')
        add('fresh-device-execution', 'SKIP', 'not performed by this verifier')
        add('numerical-output', 'SKIP', 'use compare mode with same-model/same-input CPU and NPU output records')
    elif a.mode == 'model':
        if a.model is None:
            p.error('--model is required')
        add('static-model-metadata', 'PASS', et.inspect_onnx(a.model))
    elif a.mode == 'compare':
        if None in (a.reference, a.candidate, a.atol, a.rtol):
            p.error('--reference, --candidate, --atol and --rtol are required')
        for path in [a.reference, a.candidate]:
            if path.stat().st_size > 16 * 1024 * 1024:
                raise ValueError('output record exceeds 16 MiB comparison cap')
        result = et.compare_outputs(json.loads(a.reference.read_text()), json.loads(a.candidate.read_text()), a.atol, a.rtol)
        add('provided-numeric-arrays', result['status'], result)
    if a.xrt_root is not None:
        for name in ['libxrt_coreutil.so.2', 'libxrt_core.so.2', 'libxrt_driver_xdna.so.2']:
            file_check(name, a.xrt_root / 'lib' / name)
        version_file = a.xrt_root / 'version.json'
        if version_file.is_file():
            version = json.loads(version_file.read_text()).get('BUILD_VERSION')
            add('local-xrt-version', 'PASS' if version == '2.25.37' else 'FAIL', version)
        else:
            add('local-xrt-version', 'FAIL', 'version.json missing')
        add('dynamic-runtime-selection', 'SKIP', 'files present is not proof of process library selection; capture LD_DEBUG in an isolated run')
    if a.sdk_root is not None:
        for name in ['sdk/onnxruntime/lib/libonnxruntime.so.1', 'sdk/onnxruntime/lib/libonnxruntime_vitisai_ep.so', 'peano/libpeano-lib.so.21.0git', 'include/onnxruntime_c_api.h', 'include/onnxruntime_ep_c_api.h']:
            file_check(name, a.sdk_root / 'cpp-test' / name)
        add('sdk-python-import', 'SKIP', 'C++ runtime detection does not establish Python 3.14 ABI compatibility')
    status = 'FAIL' if any(c['status'] == 'FAIL' for c in checks) else 'SKIP' if any(c['status'] == 'SKIP' for c in checks) else 'PASS'
    print(json.dumps({'mode': a.mode, 'status': status, 'checks': checks,
                      'device_execution': False, 'clean_install_validated': False}, indent=2))
    return 1 if status == 'FAIL' else 2 if status == 'SKIP' else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, TimeoutError, subprocess.TimeoutExpired) as e:
        print(json.dumps({'status': 'FAIL', 'error': type(e).__name__, 'detail': str(e)}))
        sys.exit(1)
