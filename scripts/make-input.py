#!/usr/bin/env python3
"""Create a new deterministic batch-1 input; not the historical random stream."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', required=True, type=Path)
p.add_argument('--apply', action='store_true')
a = p.parse_args()
base = ROOT / '.private-work'
dest = a.output.resolve()
if base.is_symlink() or not dest.is_relative_to(base) or dest == base:
    p.error('output must be inside this repository/.private-work')
data = struct.pack('<3072f', *[(i % 256) / 255.0 for i in range(3072)])
if a.apply:
    dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if dest.exists():
        if dest.read_bytes() != data:
            p.error('output exists with different bytes; preserved without changes')
    else:
        with dest.open('xb') as f:
            f.write(data)
print(json.dumps({'status': 'PASS' if a.apply else 'PLAN', 'shape': [1,3,32,32],
                  'dtype': 'float32-le', 'size_bytes': len(data),
                  'sha256': hashlib.sha256(data).hexdigest(),
                  'formula': 'float32((i % 256) / 255.0), i=0..3071',
                  'historical_input_reproduced': False}))
