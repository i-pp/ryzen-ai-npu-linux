# Phase 2 handoff: causal analysis and reproduction tooling

This is the original be01af5 checkpoint. Subsequent targeted Astra repairs and current validation are recorded in [astra-remediation.md](reviews/astra-remediation.md); its baseline CLI supersedes the old standalone archive-hash interface.

**Ready for the article writer to read; clean-install acceptance is not complete.** Phase-1 base commit: `ec570f0077475edecfc95ff61f59820a1380510e`. This worker wrote only this new repository. No SDK/MLIR environment execution, vendor import, reinstallation, ELF edit, system configuration change, hardware test, remote creation, push or publication occurred. C++ checking used `-fsyntax-only` against read-only headers, without a linked output.

## Useful results first

1. Historical success used **C++ ONNX Runtime C API**, after SDK Python 3.14 failed first on execstack and then CPython ABI. Python 3.12 successful provisioning is not evidenced. Parent conversation U/A/I handoff and local artifacts are reconciled in [chronology](chronology.md) and [conversation evidence](conversation-evidence.md).
2. The XRT remedy is a **Corroborated runtime-selection bundle**, not a uniquely proven ABI mismatch. Both current coreutil versions share SONAME .so.2 and export all 53 EP / 61 Dynamic Dispatch direct XRT namespace/C API import names. This bounded name check does not prove C++ semantics, versions, dynamic-only lookup or plugin initialization. [Cause/evidence table](xrt-investigation.md).
3. Static model IO is float32 `[batch_size,3,32,32]` → `[batch_size,10]`; application chooses batch=1. Original model has 386 top-level nodes, while runtime counts are transformed representations. Historical E098's 398/2/1 and inference PASS are preserved; numerical comparison was absent.
4. Both ORT headers exactly match official v1.27.0 Git blob identities. New independent probe writes actual output arrays and validates shape/finiteness; comparator requires same-model/input hashes, CPU/VitisAI provenance and explicit tolerances. Only syntax/fixtures have passed; no real output comparison exists.
5. **New clean-install blocker:** installed LLVM-AIE 22 WHEEL is cp310-cp310-manylinux_2_27/2_28, while ironenv is cp314. This corroborates historical pip-check warning. Original wheel source/hash/installation method is Unknown. Current cp314 pyxrt is exposed through a targeted venv symlink.
6. Parent collector recovered historical U logs for memlock 64 MiB/-11, root/user validation **51.0 TOPS**, actual 1 GiB limits and correct systemd drop-in. memcpy **80.19 GB/s / 1849 us** remains an A-level reading of missing material. No new benchmark is implied.
7. Local XRT three-package staging inputs are fully hashed, including the 69711164-byte plugin (`ac47b5c731931dec16d5673a64cc308ebd07f7637c8f34bba89167d63980576a`). Large SDK/ORT/Peano archive hashes remain missing; no whole-distribution hashing/download was attempted.

## Files and writer boundary

The writer should treat this snapshot's `scripts/`, `src/`, `tests/`, `artifacts/` and technical `docs/` as read-only inputs and write only `articles/`. Start from:

- [Completeness audit and article topic mapping](completeness-audit.md)
- [Claim/source distinctions](conversation-evidence.md) and [local original log excerpts](evidence-excerpts.md)
- [Reconstructed chronology](chronology.md), [runtime architecture](runtime-architecture.md), [cause analysis](xrt-investigation.md)
- [Gated clean-host recipe](reproduction-procedure.md), [verification contract](verification-design.md), [current acceptance gaps](reproducibility-status.md)
- [Manifest v2](../artifacts/manifest.json), [static analysis](../artifacts/static-analysis.json), [phase-2 supplement](../artifacts/phase2-evidence.json), [XRT input pins](../artifacts/xrt-packages.json), [validation result](../artifacts/phase2-validation.json)

Component documents cover hardware/driver, memory/permissions, XRT validation, MLIR-AIE, IRON, Python, SDK, ORT, dependencies and troubleshooting. `LICENSE` is a pending-status notice, not an invented blanket license. Raw captures remain ignored under `.private-evidence/`; `.private-work/` is reserved for future isolated staged inputs/builds/runs and is ignored. No vendor artifact is tracked.

## Tool behavior and validation

- `verify-environment.sh`, `verify-mlir-aie.sh`, `verify-iron.sh`, `verify-inference.sh`: read-only/offline JSON subchecks. Exit 0 all PASS; 1 any FAIL; 2 no FAIL but some SKIP. A historical success remains aggregate SKIP for missing fresh execution/numerical acceptance.
- `analyze-runtime.py`: static ELF/model inspection, no ldd/dlopen. `stage-xrt.py` / `stage-cpp-sdk.py`: dry plan; explicit apply, pinned input/receipt checks, safe extraction, isolated destination and drift refusal. SDK requires supplied complete hashes/license acknowledgement before apply.
- `patch-iron-python.py`, `build-probe.py`, `make-input.py`: default plans; bounded opt-in isolated changes. No vendor installer execution. `run-npu.sh` / `run-iron.py`: default plan; future execution needs both explicit flags, isolated inputs, one attempt and 180-second timeout plus grace.
- **21 offline fixture tests PASS** (`python3 -I -B -m unittest discover -s tests -v`). These cover log-stage interpretation, malformed wire data, numeric provenance/NaN/shape/tolerance, archive containment/hash/receipt drift/preservation and idempotence using tiny synthetic packages only.
- Python AST and Bash syntax PASS. New C++ source PASS under `g++ -std=c++17 -Wall -Wextra -Werror -fsyntax-only -I<SDK>/cpp-test/include src/inference-probe.cpp`.
- **Nine saved-evidence/dry-plan cases PASS against expected return states**: failing ONNX log=1, successful historical ONNX log=2, IRON without log=2, current static MLIR inventory=2, launcher/XRT staging/new build/input/IRON dry plans=0. No device opened. Exact cases are recorded in phase2-validation.json.

Integration not performed: real vendor archive staging, new probe link/load, any SDK/AIE import, IRON compilation/device execution, new ONNX Run, actual numerical comparison and an independent clean install. Fixture success does not resolve these items.

## Remaining gates and final reviewer focus

Recover/hash the large licensed inputs; compare original installer against its archive member; resolve LLVM-AIE wheel tags/provenance; recover memcpy attachment and exact DMA warning; verify effective host ACL/service limits outside the restricted namespace; then perform independently authorized clean-host integration and real numeric comparison with predeclared tolerances. Choose publication rights/license separately. [Reproducibility status](reproducibility-status.md) assigns the scope of each gate.

The canonical policy lookup is resolved through i-pp/ai-orchestration, with blob IDs in [policy provenance](policy-provenance.md). No auto-approval rejection occurred. Device nodes/service buses remain execution-environment limitations; no bypass/escalation was attempted. No original environment was changed to make verification easier.

## Later selected-input checkpoint

The [2026-10-30 current-input hash pass](collected-input-hashes.md) supersedes this snapshot's missing-large-hash/wheel-location statements for exactly five containers. SDK outer/ORT/SDK Peano and both IRON wheels are fully hashed; separate current C++/IRON baselines are frozen. This is current collection identity, not proof of historical equality or independent clean-host acceptance. Original checkpoints and the independent Astra review remain historical records.
