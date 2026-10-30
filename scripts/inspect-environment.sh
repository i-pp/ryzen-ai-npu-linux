#!/usr/bin/env bash
# Read-only metadata collection. Does not execute XRT, SDK, IRON, NPU/GPU tests.
set -euo pipefail
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 -I -B "$REPO_ROOT/scripts/collect-evidence.py" "$@"
