# IRON example and execution evidence

`programming_examples/getting_started/00_memcpy/memcpy.py` is a major independent development path, not an ONNX compatibility test. Its current source E025 uses IRON JIT and `transform_parallel`, two DMA channels, 1024-element tile size, 16777216 int32 elements, warmup=1 and five measured iterations. Column selection is delegated to the device/algorithm; eight columns are an A-level historical reading, not an explicit `num_columns=8` argument in the current script.

The current script sends a 64 MiB array and reads a 64 MiB result; the bandwidth numerator counts both directions (128 MiB). It divides by the benchmark's NPU average time, not end-to-end Python latency. The source `assert_pass(output.numpy(), input0.numpy())` uses exact `np.array_equal` when tolerances are omitted. Phase 2 verified the source and installed-wheel `aie/utils/verify.py` hashes match. This describes current source semantics; an unavailable historical attachment cannot prove every historical byte/configuration matched it.

Historical evidence is tiered:

- **U, through collector:** `aie` import, SAXPY PASS and vector_reduce_max PASS after the pyxrt visibility failure.
- **A only:** memcpy PASS, 80.19 GB/s, NPU 1673.8 us, dispatch 1737.5 us, end-to-end 1849.0 us, DMA BD reuse warnings. The numbers are arithmetically consistent with the source's transfer numerator, but that does not promote them to recovered raw measurements.
- **Unknown:** original memcpy attachment/log, exact warning text and origin, complete compiler invocation/generated artifacts/cache state, repeated-run safety and synchronization behavior.

## Future isolated execution

**Required gate:** resolve the pinned wheels and LLVM-AIE tag mismatch in [setup](mlir-aie-setup.md). **Diagnostic:** `verify-iron.sh --log <saved-output>` only evaluates supplied text; without a log it returns SKIP. It never compiles or runs anything.

`python3 -I -B scripts/run-iron.py --mlir-root <isolated-checkout> --venv <isolated-venv>` is a dry plan after checking input files. Add both `--execute --allow-device-execution` only when a new, idle test host is authorized. It refuses the preserved checkout/venv, sets a separate HOME/cache/tmp, uses system XRT independently of SDK local XRT, writes one private run directory, and terminates the process group after 180 seconds plus a five-second grace period. It runs the source's five iterations once; no automatic retry.

Capture source/package/input hashes, environment selections, compiler command and target architecture, generated MLIR/xclbin/instruction paths and hashes, warmup/cache state, stdout/stderr, exit code, output comparison and full warnings. A source or a proposed command is not an execution log. No new compilation/device run occurred in phase 2.

**Acceptance:** actual exit=0 plus exact int32 output equality, a real NPU device/runtime path, and retained compilation/run evidence. A `PASS!` line alone is only saved-log evidence. For DMA BD warnings, identify descriptor reuse/lifetime and synchronization from the exact compiler source/diagnostic, then test bounded repeated invocations and cache reuse before concluding anything about safety. The warning is neither automatically harmless nor proof of wrong output.

Successful IRON execution exercises programmable NPU compilation, transfer/dispatch and the system-XRT/driver path for that design. It weakens blanket “hardware never works” hypotheses. It leaves SDK Python ABI, Vitis EP initialization, graph partitioning and ONNX output correctness untested.
