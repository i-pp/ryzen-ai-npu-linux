#!/usr/bin/env python3
"""Plan/apply the observed interpreter-guard patch only in an isolated checkout."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEFORE = '993fa37b49ee5bab1f17afcee652c47f24517d2c234f9b2a82452f11eed0fe9c'
AFTER = 'b83e5eda436153aac9d96b4da3219629fe7821dcc4c69cfe91fccf61a69a6a2a'
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--mlir-root', required=True, type=Path)
p.add_argument('--apply', action='store_true')
a = p.parse_args()
target = (a.mlir_root / 'utils/env_install.sh').resolve()
base = ROOT / '.private-work'
if base.is_symlink() or not target.is_relative_to(base):
    p.error('target must be in an isolated .private-work checkout, never the preserved MLIR tree')
data = target.read_bytes()
current = hashlib.sha256(data).hexdigest()
if current not in (BEFORE, AFTER):
    p.error('script does not match the recorded upstream or observed local file; preserved without changes')
patched = data if current == AFTER else data.replace(b'3.12', b'3.14')
if hashlib.sha256(patched).hexdigest() != AFTER:
    p.error('patch does not produce the recorded local file')
if a.apply and current != AFTER:
    target.write_bytes(patched)
print(json.dumps({'status': 'PASS' if a.apply else 'PLAN', 'changed': a.apply and current != AFTER,
                  'effect': 'only env_install.sh interpreter guard, messages and comment; no test files',
                  'compatibility_proven': False, 'installation_performed': False}))
