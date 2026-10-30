#!/usr/bin/env python3
"""Plan one isolated 00_memcpy run. Device execution requires two explicit flags."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--mlir-root', required=True, type=Path)
p.add_argument('--venv', required=True, type=Path)
p.add_argument('--execute', action='store_true')
p.add_argument('--allow-device-execution', action='store_true')
a = p.parse_args()
mlir, venv = a.mlir_root.resolve(), a.venv.resolve()
example = mlir / 'programming_examples/getting_started/00_memcpy/memcpy.py'
site = venv / 'lib/python3.14/site-packages'
install, peano = site / 'mlir_aie', site / 'llvm-aie'
inputs = [example, venv / 'bin/python', install / 'python/aie/__init__.py', peano / 'bin/clang']
if any(not f.is_file() for f in inputs):
    p.error('isolated example/interpreter/MLIR-AIE/Peano input missing')
if not a.execute:
    print(json.dumps({'status': 'PLAN', 'example': '00_memcpy/memcpy.py', 'device_execution': False,
                      'configuration': 'source defaults: 16777216 int32, two channels, warmup=1, iters=5',
                      'runtime': 'system XRT, separate from the SDK local-XRT context'}))
    raise SystemExit(0)
base = ROOT / '.private-work'
if not a.allow_device_execution:
    p.error('--execute also requires --allow-device-execution on an authorized idle test host')
if base.is_symlink() or not mlir.is_relative_to(base) or not venv.is_relative_to(base):
    p.error('execution requires an isolated checkout and venv inside this repository/.private-work')
# A venv interpreter may intentionally point to /usr/bin/python3.14. The design,
# MLIR-AIE package and Peano compiler themselves must belong to the isolated tree.
if any(not f.resolve().is_relative_to(base) for f in [example, install / 'python/aie/__init__.py', peano / 'bin/clang']):
    p.error('design/toolchain inputs must not link into the preserved MLIR environment')
run = Path(tempfile.mkdtemp(prefix='iron-run-', dir=base))
for name in ['home', 'tmp', 'cache']:
    (run / name).mkdir(mode=0o700)
env = {'PATH': f'{venv}/bin:{install}/bin:/usr/bin:/bin', 'LC_ALL': 'C',
       'HOME': str(run / 'home'), 'TMPDIR': str(run / 'tmp'), 'XDG_CACHE_HOME': str(run / 'cache'),
       'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(install / 'python'),
       'LD_LIBRARY_PATH': str(install / 'lib'), 'MLIR_AIE_INSTALL_DIR': str(install),
       'PEANO_INSTALL_DIR': str(peano)}
timed_out = False
def interrupted(signum, frame):
    raise KeyboardInterrupt
signal.signal(signal.SIGTERM, interrupted)
with (run / 'stdout.log').open('w') as out, (run / 'stderr.log').open('w') as err:
    process = subprocess.Popen([str(venv / 'bin/python'), '-B', str(example)], cwd=run, env=env,
                               stdout=out, stderr=err, start_new_session=True)
    try:
        rc = process.wait(timeout=180)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as e:
        timed_out = isinstance(e, subprocess.TimeoutExpired)
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
        rc = 124 if timed_out else 130
result = {'exit_code': rc, 'timed_out': timed_out, 'fresh_device_execution_attempted': True,
          'clean_install_validated': False, 'log_directory': str(run.relative_to(ROOT))}
(run / 'result.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result))
raise SystemExit(rc if rc >= 0 else 1)
