# Chronological evidence checkpoint

This is a provisional historical scaffold, not an optimized installation recipe. A shell-history line records a command that was retained; it does not prove that command completed. File mtimes cannot substitute for runtime logs. Dpkg and application log timestamps do not embed a UTC offset; the journal independently reports the current host offset as +09:00, but the other timestamps are retained verbatim rather than silently normalized.

| Recorded time / order | Observation | Evidence | Confidence and limit |
|---|---|---|---|
| 2026-10-29 19:12 | Python 3.14 development/venv packages installed | dpkg source lines captured under `history-dpkg.log.txt` | Verified package event; motivation not recovered |
| 2026-10-29 19:21 | Kernel 7.0.0-42-generic installed | dpkg log | Verified package event; no fresh boot at this timestamp claimed |
| 2026-10-30 18:28:39 | System libxrt2/libxrt-npu2/libxrt-utils/libxrt-utils-npu installed at 1:2.21.75+dfsg-4 | dpkg log | Verified |
| Shell history 901–947, untimed | Driver examination, XRT installation/examine, privileged prlimit attempts, validation attempts, VTD support archive download command | `shell-history-selected.json` | Verified history content; individual output/results Unknown |
| Shell history 948–973, untimed | A process memlock adjustment, PAM limits edits including 256 MiB then 1 GiB settings, user@.service drop-in edits | `shell-history-selected.json` and present configuration | Corroborated sequence; actual error and session-refresh outcome missing |
| 2026-10-30 18:42:08+09:00 | amdxdna initializes for 0000:67:00.1 and loads `amdnpu/17f0_11/npu_7.sbin` | `kernel-npu-log.json` | Verified journal event |
| 2026-10-30 10:56 UTC mtimes | SDK installer and local py314 variant exist, differ in four Python references | source metadata, `sdk-installer-diff.json` | Verified file state, not proof of invocation/completion |
| 2026-10-30 20:30:26 (log) | 398/2 operator partition, ORT 1.27.0, EP registration and session creation PASS; XRT unavailable/compile-only message; Run fails | `ryzenai-quicktest.log:385–386,740–752` | Verified historical output |
| Associated failed trace, no embedded time | `openat` of `/usr/lib/x86_64-linux-gnu/libxrt_coreutil.so.2` succeeds | `ryzenai-quicktest.strace:49` | Verified trace content; association is filename/context based |
| 2026-10-30 20:45:13 (log) | Local libxrt_coreutil/core/driver_xdna initialization; 398 NPU and 2 VITIS_EP_CPU operators, one NPU subgraph reported; Inference/Quicktest PASS | `ryzenai-xrt225.log:387,794–799,1151,1154,1227–1234` | Verified historical output; no numeric oracle |
| Current capture 2026-10-30 12:57:55 UTC | Existing working launcher prioritizes local XRT plus SDK/Peano libraries; both venvs are 3.14.4; process limit 1 GiB | capture and source metadata | Verified current state; no new inference |

The MLIR-AIE/IRON setup and benchmark belong between these events in the full history, but their command timestamps and original result logs are not yet recovered. They must not be assigned invented times. Current source and package revisions establish a snapshot, not the entire installation history.

The paired runtime records support further investigation of XRT selection. They do not yet isolate `XILINX_XRT`, library path, local base library, and driver plugin as independent causal factors. The successful log still contains three symbol-lookup diagnostics, preserved in the excerpts for review.
