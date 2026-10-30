# Reconstructed engineering chronology

This is history, not the optimized installation order. Times below are conversation UTC timestamps unless explicitly labelled file/runtime timestamps. The collector's U/A distinction is preserved in [conversation evidence](conversation-evidence.md). Current files establish the final state, not when every change occurred. The original [phase-1 chronology](chronology-evidence.md) remains a capture-time record.

## 1. Detect hardware before choosing a runtime

- **Objective / assumptions:** run AI on the EVO-X3 NPU; determine whether PCI, kernel and firmware already support it.
- **Approach / commands:** inspect PCI, kernel, module and device permissions; `lspci -nnk`, module/journal inspection, XRT availability check. Untimed shell history and U at 09:26–09:27 retain portions of the commands, not every invocation.
- **Observed behavior / errors:** amdxdna and the render-owned node existed; the user was already in render. Initial kernel was 7.0.0-38. XRT was not yet installed.
- **Hypotheses / investigation:** distinguish absent user-space XRT from absent hardware/driver; no evidence supported adding another kernel driver.
- **Evidence / cause:** U initial-state logs; phase-1 later confirms in-tree amdxdna and FW path. Verified states at different times; no single global cause yet.
- **Corrective action / verification:** Ubuntu XRT 2.21.75 packages subsequently installed (dpkg event 18:28:39 local log timestamp). Runtime examination progressed to memory allocation.
- **Uncertainty:** exact complete APT transcript and motivation for the later kernel update are not recovered.

## 2. Memory mapping, limits and validation data

- **Objective / assumptions:** make XRT enumerate and validate without routinely using root.
- **Approach / commands:** compare shell limits, `xrt-smi examine`, and historical `sudo prlimit --memlock=unlimited:unlimited -- xrt-smi examine`; later examine actual manager/service process limits and configured unit properties.
- **Observed behavior / errors:** 64 MiB mapping failed with -11 under the initial approximately 8 MiB limit. Root plus unlimited detected the device. Raising one's own hard limit to 128 MiB failed with EPERM. Validation initially lacked a support archive, separately for root and ordinary-user cache locations.
- **Hypotheses / investigation:** memlock became a strong explanation, although sudo plus unlimited changed more than one variable. Follow the actual process limit rather than a unit-display value alone.
- **Evidence / cause:** U 09:28–09:51; present PAM file E012, correct drop-in E014, saved process limits. Corroborated causal explanation; a strict one-factor experiment was not retained.
- **Corrective action / verification:** PAM evolved through 256 MiB to 1 GiB; an initially misplaced systemd file was superseded by `/etc/systemd/system/user@.service.d/99-memlock.conf` with 1G. U logs show actual shell and manager limits at 1 GiB and root/user validation PASS, each reporting GEMM 51.0 TOPS.
- **Uncertainty:** exact login/reboot timing and which step changed each running process are Unknown. Wrong-path file is absent now; its historical deletion command/time is not recovered. The kernel is 7.0.0-42 by 09:43Z.

## 3. Bring up MLIR-AIE/IRON independently

- **Objective / assumptions:** establish a programmable NPU path before diagnosing a larger ONNX stack.
- **Approach / commands:** `source utils/env_install.sh` initially fails on missing 3.12; inspect explicit minor-version guard. Later U shows Python 3.14.4 and installed MLIR-AIE/LLVM-AIE metadata.
- **Observed behavior / errors:** current local env script accepts 3.14; aie import succeeded historically, but pip check retained a platform warning. First memcpy produced CPUOnlyTensor/Unsupported device because pyxrt was invisible to the venv.
- **Hypotheses / investigation:** distinguish a Python ABI problem from import-path isolation. System Python could import the cp314 APT module while ironenv could not.
- **Evidence / cause:** U 10:04–10:22; E019–E028; current pyxrt symlink and wheel metadata. Venv visibility is Corroborated. Current LLVM-AIE wheel declares cp310 tags, explaining why ordinary fresh pip installation cannot be assumed.
- **Corrective action / verification:** a targeted pyxrt symlink exists now. U later records SAXPY/reduce PASS; A reads memcpy PASS, bandwidth/timing and DMA warnings from unavailable material.
- **Uncertainty:** exact guard-edit, wheel-acquisition and pyxrt-link commands/times; LLVM-AIE tag override/installation method; memcpy attachment and repeated-run synchronization safety. A complete source build is not evidenced; submodules are uninitialized.

## 4. Try SDK Python 3.14, then change API boundary

- **Objective / assumptions:** test SDK 1.8 without replacing the host Python.
- **Approach / commands:** local installer variant substitutes 3.14 for four 3.12 references; inspect wheel contents; import ORT.
- **Observed behavior / errors:** executable-stack error, then unresolved `_PyThreadState_UncheckedGet` after a historical stack-flag change. Python 3.12 had no APT candidate in the shown session.
- **Hypotheses / investigation:** broad wheel tags conceal native ABI constraints. ELF stack policy and CPython ABI are separate issues.
- **Evidence / cause:** U 10:57–11:06; E050/E051; phase-2 original ZIP GNU_STACK RWE, current binding RW and its undefined import. The binding/3.14 incompatibility is supported, but not every SDK module has been tested.
- **Corrective action / verification:** use the C API from C++ instead. No successful SDK Python run or 3.12 provisioning is evidenced.
- **Uncertainty:** complete vendor installer transcript and dependency resolution. Current `.orig` is also RW and must not be treated as an untouched backup.

## 5. Assemble C++ runtime and compiler dependencies

- **Objective / assumptions:** call ORT without loading its Python binding.
- **Approach / commands:** acquire official v1.27.0 C and EP headers; compile provider enumeration and EP registration code. Initialize OrtEnv/logger before registering the EP. Include SDK library and SDK Peano paths.
- **Observed behavior / errors:** missing EP header; logger error; missing compiler dependency; then missing `libpeano-lib.so.21.0git`.
- **Hypotheses / investigation:** link-time success does not establish the later EP compiler's transitive library closure. Inspect ldd/readelf and SDK wheel contents.
- **Evidence / cause:** U 11:11–11:23; E033–E042; phase-2 exact official header blob matches; xcompiler `DT_NEEDED` on Peano.
- **Corrective action / verification:** extract SDK Peano from `lnx64.o/tools/peano/lib`, use SDK+Peano `LD_LIBRARY_PATH`; provider enumeration and EP registration succeed.
- **Uncertainty:** original full compiler command/source evolution is not fully recovered in this handoff. New build commands are explicitly reconstructions, not claimed historical invocations.

## 6. Compile the model, fail at Run, select a local runtime

- **Objective / assumptions:** move beyond EP/session construction to actual inference.
- **Approach / commands:** run deterministic-input C++ quicktest; inspect its failure log, strace, ELF dependencies and system/runtime context.
- **Observed behavior / errors:** EP registration and session creation succeed; compilation assigns NPU/CPU work; compile-only warning appears; `Run` fails on an unconstructed tensor. Trace opens system coreutil.
- **Hypotheses / investigation:** investigate runtime selection/initialization rather than taking “XRT not installed” literally. The earlier driver-stub hypothesis is not a proven root cause.
- **Evidence / cause:** E096/E097 and U/A 11:27–11:38. Exact ABI/symbol failure is not established. Both current coreutil implementations export the bounded set of direct XRT import names.
- **Corrective action / verification:** U 11:44 extracts XRT base/npu/plugin DEBs locally. Set `XILINX_XRT` and local-XRT:SDK:Peano paths; E098 and U 11:45 show local libraries initialize and inference/quicktest PASS, with 398/2/1 reported in E098.
- **Uncertainty:** no controlled A/B isolation of environment variable, coreutil and plugin; no numeric output comparison or independent device trace. A successful API return is not a validated model prediction.

## 7. Preserve and reconstruct

- **Objective / assumptions:** turn a working historical state into inspectable evidence and a gated reproduction procedure.
- **Approach / commands:** phase 1 captures read-only evidence at 12:57:55 UTC. Phase 2 statically reads ELF/model/package metadata and tests new helpers with fixtures. No original environment is executed, rebuilt, patched or installed into.
- **Observed behavior / errors:** namespace hides device nodes and denies systemd buses; this does not negate host logs. Clean-install inputs and several historical logs remain incomplete.
- **Hypotheses / investigation:** separate history, current state and a new isolated experiment; preserve evidence confidence and absent data.
- **Evidence / cause:** phase-1 checkpoint, phase-2 evidence, validation record and audit. No new hardware success claimed.
- **Corrective action / verification:** prepare opt-in staging, new C++ output probe, offline PASS/FAIL/SKIP verifiers, causal report and completeness audit. Syntax/fixture results are recorded separately from device tests.
- **Uncertainty:** [reproducibility gates](reproducibility-status.md) remain. Article drafting and independent Astra review are subsequent roles.
