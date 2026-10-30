# Python compatibility and the C++ bypass

Both preserved venvs use **Python 3.14.4**, Verified by phase-1 interpreter probes and `pyvenv.cfg`. SDK Python 3.12 was an initial instruction-sheet value and a vendor requirement, not the proven successful interpreter in this case.

## MLIR-AIE/IRON

- The upstream script at the pinned commit defaults to Python 3.12 and explicitly rejects another minor version. The current local file changes the guard, diagnostic text and comment to 3.14. Simply setting `PYTHON=python3.14` against the original script does not work. U history reports those failures.
- Installed mlir-aie 1.4.5.dev113+ge28f6dc carries a **cp314-cp314-manylinux_2_35_x86_64** WHEEL tag and metadata `Requires-Python >=3.11`. Its Python>=3.12 branch declares NumPy >=2.5.3,<3. NumPy 2.5.4 is consistent with that range; it is not uniquely required.
- U history reports `aie` import success and a surviving `pip check` platform warning for LLVM-AIE. There was no fresh import or pip check here; static metadata cannot resolve that warning.
- Follow-up located the original-name LLVM-AIE22 candidate in pip HTTP cache: its filename is `llvm_aie-22.0.0.2026102001+4f5df13d-py3-none-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`, while its internal WHEEL is cp310-cp310. WHEEL/METADATA match the installed files. Preserved pip source selects candidates by filename tags and checks installed support using internal WHEEL tags. This supports normal selection followed by a platform warning; forcing/renaming was not established. The earlier inference that a cp310 override is necessarily required is superseded. Full wheel hash, exact historical command and fresh native acceptance remain pending. See [retained inputs](remaining-inputs.md).
- U history shows cp314 pyxrt imported by system Python but initially hidden from ironenv. Current phase-2 state confirms a single venv symlink to `/usr/lib/python3/dist-packages/pyxrt.cpython-314-x86_64-linux-gnu.so`. The exact time/method it was added is not recovered.
- The existing `utils/env_setup.sh` is not an offline inspection tool: it runs `xrt-smi examine` and imports pyxrt. Do not source it during preservation.

`patch-iron-python.py` can reproduce the exact observed env-script bytes only in a new `.private-work` checkout with the expected before/after SHA-256. It deliberately does not reproduce the unrelated changes in `test/test_kernel_workflows.py`. The patch changes acceptance criteria, not native-extension compatibility. Wheel acquisition and a new environment test remain required.

## SDK Python experiment

The vendor-style installer E050 hardcodes 3.12. E051 substitutes four Python references/check values for 3.14. The historical 3.14 import failed first on an executable-stack requirement, then—after an ELF flag edit—on unresolved `_PyThreadState_UncheckedGet`. The [conversation U evidence](conversation-evidence.md) establishes two separate failures, rather than a successful Python workaround.

New static evidence strengthens that account:

| Check | Result and limit |
|---|---|
| ORT wheel WHEEL/METADATA | `py3-none-linux_x86_64`, `Root-Is-Purelib: true`, Python>=3.6, but contains `onnxruntime_pybind11_state.so`. Package tags do not prove its native ABI is compatible. |
| VOE wheel | Contains `pyflexmlrt.cpython-312-x86_64-linux-gnu.so` despite broad wheel tag. |
| Original ORT wheel member ELF program header | GNU_STACK flags 7 (RWE), read directly from ZIP without loading it. |
| Current installed binding | GNU_STACK RW, still imports `_PyThreadState_UncheckedGet`; that name is absent from `/usr/bin/python3.14`'s dynamic exports. The historical import error is stronger runtime evidence. |
| Current `.so.orig` | Also RW now. The filename alone is not an unmodified-original guarantee; do not reconstruct original bytes from it. |

No ELF flags were changed by this project. Do not turn the historical `patchelf` attempt into a required installation step, and do not weaken host stack policy to run this experiment.

## Python 3.12 status

U history reports no APT candidate at the time. Current bounded searches also did not find 3.12 in standard locations. Neither establishes absence from every host path. Provisioning 3.12 in a separate prefix/container with the right system runtime is **Conditional** if the Python SDK API is needed, and **not yet reproduced**. Never replace `/usr/bin/python3`, remove the system Python, or claim that SDK Python execution succeeded.

The historical successful route is C++ → ONNX Runtime C API → Vitis AI EP. It avoids the failing SDK Python binding; it does not demonstrate general Python 3.14 support for the SDK.
