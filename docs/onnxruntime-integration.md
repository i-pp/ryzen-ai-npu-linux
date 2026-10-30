# C++ ONNX Runtime integration

E035 is a C++17-style application calling the **ONNX Runtime C API**, not the C++ wrapper API. It creates OrtEnv, registers `VitisAI`, creates a session, supplies one float32 `input` of shape [1,3,32,32], queries output names/count and calls `Run`. Input values use mt19937 seed 42 and uniform_real_distribution. It prints names, releases outputs and returns success; it does not query output shape/data or compare numerical values.

The model is SDK quicktest `test_model.onnx`, SHA-256 `7a78c7e85bac3a0681e3d2f77e69093a761e1c8f62f7fc65ff5ce3e1b82c5ba3`. Static wire inspection finds producer `vai_q_onnx`, IR 7, default opset 13, input float32 `[batch_size,3,32,32]`, output float32 `[batch_size,10]`, 386 top-level nodes and no top-level external initializers. This is metadata inspection rather than ONNX checker/shape inference or executed output evidence. Batch=1 is the historical application's chosen input shape.

## Headers and reconstruction build

The preserved `cpp-test/include` contains both `onnxruntime_c_api.h` and its included `onnxruntime_ep_c_api.h`. Their Git blob IDs match the official [v1.27.0 files](https://github.com/microsoft/onnxruntime/tree/v1.27.0/include/onnxruntime/core/session): `793cdd505aaa3f362e2d29dbae2e8b00e31742f8` and `6824b85ba300114ee1fd2db64098b17f5f65b80b`. SHA-256 values are in [static-analysis.json](../artifacts/static-analysis.json). API version is 27.

The original exact compiler command is not fully recovered. The following is a **reconstruction for the newly authored probe**, implemented by `build-probe.py`, using a staged isolated SDK:

```text
g++ -std=c++17 -O2 -Wall -Wextra -I<SDK>/cpp-test/include \
  src/inference-probe.cpp -L<SDK>/cpp-test/sdk/onnxruntime/lib \
  -Wl,-rpath,$ORIGIN/sdk/onnxruntime/lib -lonnxruntime \
  -o <SDK>/cpp-test/inference-probe
```

The `$ORIGIN` linker argument must be passed literally, not expanded by the shell. The Python helper passes an argv array and refuses to build in the original SDK. It records source/header/runtime/compiler identities and refuses to overwrite a mismatched build. The historical executable instead embeds an absolute RUNPATH to its original SDK directory; do not copy it and assume it is relocatable.

EP/compiler libraries are loaded later, so linking `-lonnxruntime` and resolving its direct dependencies is not sufficient. Use local XRT → SDK libraries → SDK Peano in the launch environment. Do not substitute IRON's LLVM-AIE 22 toolchain for the SDK's `libpeano-lib.so.21.0git` merely because both are called Peano. See [the runtime graph](runtime-architecture.md).

## New numerical probe

`src/inference-probe.cpp` is new code, not a redistributed vendor/historical source. It accepts absolute model/input/output paths, selects CPU or VitisAI, reads exactly 3072 little-endian float32 input values, validates an actual float32 [1,10] output, rejects nonfinite values and writes every output value with provenance fields. `make-input.py` generates a new deterministic input formula; it does not reproduce the old random stream byte-for-byte.

The same serialized input must be used for CPU and NPU calls. `run-npu.sh` validates the supplied model/input hashes, fixes the runtime environment, records exit/log/hash information and requires an isolated tree plus explicit device-execution flags. Numerical comparison is a separate step with operator-chosen, justified tolerances. This probe has passed C++ syntax checking against the matched read-only headers, **not a link, load, device run or numeric acceptance test** in phase 2.

## Astra output/identity repair

`build-probe.py` now rejects output symlinks (including dangling ones), unpaired/unowned outputs and concurrent builders under an exclusive lock. It builds to a private temporary location and publishes app/receipt without replacement. One absolute compiler file/hash and the same fixed environment are used for version and build. The probe uses the independent `exclusive-output.hpp` writer: a complete private JSON record is linked into the requested destination without replacement; concurrent or existing/symlink outputs cannot be truncated. Only a standalone writer fixture has been linked/executed here, not the SDK probe.
