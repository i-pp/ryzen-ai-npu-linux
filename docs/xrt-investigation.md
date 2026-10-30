# Compile-only failure: evidence and causal limits

The successful change was a **runtime-selection bundle**: local XRT 2.25.37, its XDNA user-space plugin, `XILINX_XRT`, and library-path precedence. It is Corroborated as the remedy for this case. A particular missing XRT symbol, an ABI-layout incompatibility, or one environment variable as the sole cause is **not established**.

## Observations

| Observation | Evidence | Confidence and implication |
|---|---|---|
| Failed run registered Vitis AI EP, partitioned/compiled the model and created a session, then skipped execution and failed `Run` | E096, [excerpts](evidence-excerpts.md), lines 385–386 and 740–752 | Verified historical output. Compilation/registration was insufficient for inference. |
| Failed trace successfully opened system `libxrt_coreutil.so.2` | E097:49 | Verified `openat` result. It proves neither complete initialization nor compatibility. |
| Successful log initializes local coreutil/core/driver_xdna and completes inference | E098:387,1151,1154,1227–1234 | Verified historical log, corroborated by conversation U at 11:45Z. No new run in this project. |
| Both coreutil implementations have SONAME `libxrt_coreutil.so.2` | [static analysis](../artifacts/static-analysis.json) | Verified current ELF data. A matching filename/SONAME cannot select a compatible implementation by itself. |
| EP imports 53 XRT-namespace/C API names; Dynamic Dispatch imports 61. Both system and local coreutil export all those unversioned names | Same artifact, `xrt_namespace_imports` | Verified bounded name comparison. This does **not** test symbol versions, C++ object layout, semantics, `dlsym`-only lookups, plugins, or initialization. It does not prove ABI compatibility. |
| EP has a direct `DT_NEEDED` on coreutil but no RPATH/RUNPATH | Same artifact, `elf.ep` | Verified static dependency. The quicktest's RUNPATH to ORT is insufficient to describe the entire graph. |
| `libxcompiler-mlir-e2e.so` directly needs SDK Peano `libpeano-lib.so.21.0git` | Same artifact, `elf.xcompiler` | Verified. IRON's separately installed LLVM-AIE 22 package is not a substitute established by this case. |

The loader's normal search uses RPATH when applicable, `LD_LIBRARY_PATH`, RUNPATH, the cache and default directories. RUNPATH applies to direct dependencies rather than being inherited throughout the graph. These details explain why a link command or `ldd quicktest` alone cannot establish the EP's later dynamic-load behavior. See [ld.so(8)](https://man7.org/linux/man-pages/man8/ld.so.8.html) and the recorded ELF graph; secure execution and already-loaded objects can change the practical result.

## Reconstructed mechanism

The original launcher E036 starts a new process with `XILINX_XRT=<local-root>` and exactly `<local-root>/lib:<SDK-lib>:<SDK-Peano>` as `LD_LIBRARY_PATH`. It does not append the caller's old value. Local coreutil, core and `libxrt_driver_xdna.so.2` then initialize in E098 and inference completes. This is consistent with avoiding an unsuitable system-runtime context while preserving system XRT for the independent IRON path.

What is missing is a controlled matrix holding model, application, caches, limits, libraries and process environment constant while varying only runtime root, coreutil, plugin or environment variable. The failed `strace` is not a failed-run `LD_DEBUG` transcript; `openat=3` must not be rewritten as proof that all constructors or driver discovery succeeded. Source for the exact SDK binary's compile-only decision has not been matched, so the internal branch and its returned error remain Unknown.

The successful log contains lookup diagnostics for `compile_onnx_model_vitisai_ep_v3`, `profiler_start` and `profiler_stop`. They were nonfatal to that process's reported completion; their optionality and all affected features are not established. `No driver detection supported` also appears in the successful conversation log. Neither string is a standalone failure oracle. Earlier suggestions that a driver-detection stub made execution impossible remain superseded hypotheses.

## Safe diagnostic sequence

1. **Diagnostic:** read ELF `NEEDED`, SONAME and RPATH/RUNPATH using `readelf`; run `scripts/analyze-runtime.py` on explicit read-only inputs.
2. **Diagnostic:** compare XRT-provided imported names with both versions. Retain the limited meaning of that comparison.
3. **Diagnostic:** replay E096/E098 with `verify-inference.sh --log ...`; do not rerun the preserved application.
4. **Conditional, future isolated host only:** run one explicitly authorized process through `run-npu.sh --execute --allow-device-execution`. Capture separate stdout/stderr, exit code, hashes, `LD_DEBUG=libs` and selected configuration. A loader trace is a real process invocation; it is not an offline inspection.
5. **Optional, future diagnostic experiment:** capture `strace -f -e trace=openat,ioctl,mmap` on that isolated application. Trace overhead changes timing; the trace is unsuitable as a performance measurement.

Do not replace system packages or kernel drivers to repeat this investigation. The current environment is evidence, and clean-install validation is still outstanding.
