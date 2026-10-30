# Historical runtime evidence excerpts

These are sanitized excerpts, not fresh test results. Source line numbers refer to the preserved original files. ANSI color sequences and trailing whitespace are removed; home/workspace paths are aliases. Complete original logs and hashes are private. The runtime timestamps carry no explicit UTC offset; do not silently convert them.

## ryzenai-quicktest.log

```text
385: 2026-10-30 20:30:26.507659199 [I:onnxruntime:, stat.cpp:198 stat.cpp]    NPU   398
386: 2026-10-30 20:30:26.507688870 [I:onnxruntime:, stat.cpp:198 stat.cpp] VITIS_EP_CPU     2
740: ONNX Runtime: 1.27.0
741: Vitis AI EP registration: PASS
742: INFO: [VAIP-VAIML-CUSTOMOP] XRT is not installed. This InferenceSession generates model binaries only. The session handle can not be used for inference run.
749: 2026-10-30 20:30:26.576929560 [W:onnxruntime:, custom_op.cpp:651 custom_op.cpp] Skipping execution in compile-only mode
751: api->Run( session, nullptr, input_names, inputs, 1, output_name_ptrs.data(), output_count, outputs.data()): Non-zero status code returned while running DequantizeLinear node. Name:'output_DequantizeLinear' Status Message: the ort_value must contain a constructed tensor or sparse tensor
752: ONNX session creation: PASS
```

## ryzenai-quicktest.strace

```text
46: 147479 openat(AT_FDCWD, "<WORKSPACE>/ryzen-ai-1.8.0/cpp-test/sdk/onnxruntime/lib/libxrt_coreutil.so.2", O_RDONLY|O_CLOEXEC) = -1 ENOENT (そのようなファイルやディレクトリはありません)
47: 147479 openat(AT_FDCWD, "<WORKSPACE>/ryzen-ai-1.8.0/cpp-test/peano/libxrt_coreutil.so.2", O_RDONLY|O_CLOEXEC) = -1 ENOENT (そのようなファイルやディレクトリはありません)
49: 147479 openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/libxrt_coreutil.so.2", O_RDONLY|O_CLOEXEC) = 3
133: 147479 openat(AT_FDCWD, "cpp-test/samples/quicktest/test_model.onnx", O_RDONLY) = 3
```

## ryzenai-xrt225.log

```text
387:     171887:	calling init: <WORKSPACE>/ryzen-ai-1.8.0/xrt-2.25.37/opt/xilinx/xrt/lib/libxrt_coreutil.so.2
410:     171887:	<WORKSPACE>/ryzen-ai-1.8.0/cpp-test/sdk/onnxruntime/lib/libonnxruntime_vitisai_ep.so: error: symbol lookup error: undefined symbol: compile_onnx_model_vitisai_ep_v3 (fatal)
411:     171887:	<WORKSPACE>/ryzen-ai-1.8.0/cpp-test/sdk/onnxruntime/lib/libonnxruntime_vitisai_ep.so: error: symbol lookup error: undefined symbol: profiler_start (fatal)
412:     171887:	<WORKSPACE>/ryzen-ai-1.8.0/cpp-test/sdk/onnxruntime/lib/libonnxruntime_vitisai_ep.so: error: symbol lookup error: undefined symbol: profiler_stop (fatal)
793: 2026-10-30 20:45:13.829252265 [I:onnxruntime:, stat.cpp:198 stat.cpp] [Vitis AI EP] No. of Operators :
794: 2026-10-30 20:45:13.829263256 [I:onnxruntime:, stat.cpp:198 stat.cpp]    NPU   398
795: 2026-10-30 20:45:13.829266826 [I:onnxruntime:, stat.cpp:198 stat.cpp] VITIS_EP_CPU     2
797: 2026-10-30 20:45:13.829272326 [I:onnxruntime:, stat.cpp:198 stat.cpp] [Vitis AI EP] No. of Subgraphs :
798: 2026-10-30 20:45:13.829274946 [I:onnxruntime:, stat.cpp:198 stat.cpp]    NPU     1
799: 2026-10-30 20:45:13.829277556 [I:onnxruntime:, stat.cpp:198 stat.cpp] Actually running on NPU      1
1151:     171887:	calling init: <WORKSPACE>/ryzen-ai-1.8.0/xrt-2.25.37/opt/xilinx/xrt/lib/libxrt_core.so.2
1154:     171887:	calling init: <WORKSPACE>/ryzen-ai-1.8.0/xrt-2.25.37/opt/xilinx/xrt/lib/libxrt_driver_xdna.so.2
1227: ONNX Runtime: 1.27.0
1228: Vitis AI EP registration: PASS
1229: ONNX session creation: PASS
1230: Output count: 1
1231: Running inference...
1232: Inference: PASS
1233: Output[0]: output
1234: Quicktest: PASS
```
