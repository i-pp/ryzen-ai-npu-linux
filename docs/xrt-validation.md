# System XRT validation

The system packages remain Ubuntu XRT **1:2.21.75+dfsg-4**. Local SDK XRT 2.25.37 is a separate context. Do not run the SDK launcher and interpret its version as the system package version.

The parent conversation collector recovered two U diagnostic results: root/Performance at 09:32Z and ordinary-user/Default at 09:44Z both report all tests PASS and GEMM **51.0 TOPS**. Their reported latency/throughput differ (50.0 us/74904.0 op/s versus 46.0 us/76330.0 op/s). These are historical XRT diagnostic outputs through the collector, not fresh measurements, ONNX-model throughput, or a generally reproducible performance claim. Original local validation files and full test input configuration are still missing. See [the U source links](conversation-evidence.md).

**Diagnostic:** inspect selected package versions and `command -v xrt-smi` without invoking device tests. `verify-environment.sh` checks package metadata, PCI and current process limits only.

**Conditional, future authorized host execution:** with correct ordinary-user access/limits, record `xrt-smi --version`, `xrt-smi examine` and `xrt-smi validate` with one bounded attempt, for example `timeout --kill-after=5s 180s xrt-smi validate`. Save stdout, stderr, exit code, device, mode, firmware and exact test configuration. These commands can open the device and are not part of read-only offline verification.

The historical validator required `xrt_smi_strx.a` in the invoking user's `~/.local/share/xrt/2.21.75/amdxdna/bins/`. Root and ordinary user use different homes; downloading to root's cache did not satisfy the user run. The retained user support archive is E016; verify its SHA-256 before a future test. Acquisition source and expected hash are in [dependencies](dependencies.md). No archive was downloaded or copied to a system/root path in this project.

A validation PASS establishes that that diagnostic's kernels and runtime path completed under its conditions. It does not establish MLIR wheel compatibility, SDK Python import compatibility, ONNX EP execution or numerical model correctness. Preserve failed tests and mode-specific context instead of publishing just the largest throughput number.
