# Evidence-led troubleshooting

| Symptom | Diagnostic and likely interpretation | Action class / safe next step |
|---|---|---|
| No `/dev/accel` in agent/container | Check namespace visibility versus host PCI/journal; phase-1 host logs and runtime success exist | Diagnostic; request later host-shell evidence, do not infer physical absence or install a driver from inside the restricted namespace |
| 64 MiB mmap -11 with low memlock | Inspect actual process soft/hard limits and invoking uid/session; historical 8 MiB/1 GiB evidence | Conditional administrator/session work only on isolated host; [limit procedure](memory-and-permissions.md) |
| `prlimit` EPERM | User cannot exceed inherited hard ceiling; root/unlimited changed multiple factors historically | FailedHistorical; inspect login/service inheritance rather than repeating raises |
| Unit configuration says 8 MiB while process shows 1 GiB | Parsed settings, existing manager and child limits are different observations | Diagnostic; inspect `/proc` and effective child, not just systemctl output |
| Validation archive missing | The invoking user's cache differs from root's; file/version/hash must match XRT | Conditional manual acquisition of the pinned support archive, no routine root validation |
| IRON installer rejects 3.14 | Upstream has a 3.12 equality guard, not only a default variable | Diagnostic; exact isolated guard patch remains experimental; do not replace system Python |
| `aie` exists but `Unsupported device: npu` / CPUOnlyTensor | In U evidence the cp314 pyxrt module was hidden from the venv | Conditional targeted visibility fix in a new venv only, validate ABI/path first |
| LLVM-AIE “not supported on this platform” | Installed WHEEL currently cp310, venv cp314 | Unresolved fresh-install gate; recover proper wheel/provenance, never silently force foreign-ABI installation |
| SDK import executable-stack error | Original binding GNU_STACK RWE; historical flag edit then exposed ABI error | FailedHistorical; no current ELF edit or security-policy relaxation; use C++ route or separately provision supported Python |
| `_PyThreadState_UncheckedGet` undefined | Native SDK binding/current Python ABI mismatch supported by U and static import/export evidence | Conditional Python3.12 branch unperformed; C++ bypass independently documented |
| C API header includes missing EP header | ORT API27 header requires matching onnxruntime_ep_c_api.h | Required matched v1.27.0 pair with recorded hashes |
| DefaultLogger not registered | Historical registration preceded OrtEnv/logger initialization | Required source ordering: CreateEnv, then EP/session options registration |
| Missing xcompiler or Peano at EP load | Later dynamic dependencies exceed quicktest's direct link closure | Diagnostic readelf; Required SDK and SDK Peano paths. Do not substitute IRON Peano22 without proof |
| XRT “not installed” despite installed packages | System coreutil can be opened yet EP remains compile-only | Diagnostic [XRT investigation](xrt-investigation.md); test full local runtime bundle only on new authorized host |
| `undefined symbol: profiler_start/stop` / driver-detection message | Also observed in successful logs | Preserve diagnostics; judge exit/Run/output/selected path and feature scope, not the string alone |
| NPU partition counts but no output | Compilation/partitioning does not prove Run completion | FAIL for inference acceptance; retain failing log; numerical comparison remains separate |
| Numeric comparator fails | Wrong provenance/shape/nonfinite values or actual tolerance violation | Preserve both records and exact criterion; do not relax tolerances merely to pass |
| Helper reports drift/existing destination | Receipt no longer matches; no automatic destructive repair | Diagnostic; inspect preserved tree/partial and choose a new isolated destination, no changes to originals |

No generic error string proves one root cause. Read the corresponding source/log and the [verification level](verification-design.md), then act only on the selected branch. No automatic hardware retry, package reinstall or system configuration repair occurs here.
