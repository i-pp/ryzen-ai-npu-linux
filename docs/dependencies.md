# Dependencies, installed packages and acquisition

Requirements below are scoped to a path. An installed version is not automatically a requirement. Package versions and metadata are in the [manifest](../artifacts/manifest.json), [phase-2 supplement](../artifacts/phase2-evidence.json) and [ELF analysis](../artifacts/static-analysis.json).

| Layer | Necessary or explicitly declared | Observed but not established as minimal/required | Acquisition or unresolved issue |
|---|---|---|---|
| Host/kernel | supported PCI function, amdxdna, loaded matching firmware, effective device access and sufficient memlock | kernel 7.0.0-42, 1 GiB chosen limit; no threshold/minimal-kernel experiment | Ubuntu packages; exact old packages/firmware availability not archived |
| Offline project tooling | Python >=3.12 standard library, Bash, binutils `readelf`/`nm`, dpkg-deb for future staging; g++ C++17 for new probe | observed GCC 15.2/Clang 21/CMake 4.2/Ninja 1.13 | No CMake/Ninja needed by this project's single-source C++ build |
| System XRT/IRON | system XRT 2.21.75 libraries and cp314 pyxrt for this snapshot | five installed XRT packages; support archive for validation only | Ubuntu APT metadata; VTD support archive pinned by E016 hash |
| MLIR-AIE/IRON | matching cp314 MLIR-AIE and Peano inputs; declared NumPy/ml_dtypes/cloudpickle ranges | observed versions are pins, not unique requirements | Both original-name wheel candidates located in pip HTTP cache; complete hashes/exact acquisition URL and fresh native validation pending. LLVM-AIE filename/internal tags differ; [follow-up](remaining-inputs.md). |
| SDK Python path | vendor installer hard-requires Python 3.12; ORT metadata requires voe==1.8.0 plus NumPy>=1.21.6, coloredlogs, flatbuffers, packaging, protobuf, sympy | Python 3.14 replacement guard permitted installation but not import; full SDK pulls many ML/CUDA dependencies | Python 3.12 provisioning on Ubuntu 26.04 remains a separate unperformed task |
| C++ ORT path | ORT 1.27.0 library and matched C/EP headers; compiler/Vitis libraries; SDK Peano 21.0git; local XRT base/plugin context | SDK Python venv, torch, transformers, datasets, CUDA/NVIDIA wheels are not demonstrated prerequisites for this C++ application | C++ archive, SDK llvm_aie wheel, quicktest archive; two large-input hashes deferred |
| Host C++ shared libraries | ELF imports include libc, libgcc, libstdc++, libuuid, zlib, zstd, ncurses and tinfo, as selected by the loader | XRT base package declares additional OpenCL/Boost/OpenSSL/Python dependencies that the shown coreutil subset does not itself import | Local extraction does not satisfy or register DEB dependencies; validate the actual selected ELF closure on a clean host |

The source-build toolchain and submodules are **Conditional** for an MLIR-AIE source build. They are not proven necessary for the observed prebuilt-wheel environment. No successful full source build is evidenced. DKMS installation is not an established requirement here: the observed host uses the in-tree driver and history reports an empty DKMS list.

## Artifact acquisition ledger

| Artifact | Source/pin | Integrity/status |
|---|---|---|
| `ryzen_ai-1.8.0.tgz` | [AMD authenticated download form](https://account.amd.com/en/forms/downloads/xef.html?filename=ryzen_ai-1.8.0.tgz), linked by AMD Linux instructions | Local 7.8 GB archive metadata E018; complete SHA-256/acquisition receipt not captured. Manual authentication/terms may be required; no scripted bypass. |
| `RAI_1.8_Linux_NPU_XRT.zip` | [Official AMD download](https://download.amd.com/opendownload/RyzenAI/Driver/RAI_1.8_Linux_NPU_XRT.zip) | E017 SHA-256 `ea37ce2ff46ae20e64a081c38fc45b3bae183e488f293543c811f4c05186d2df`; DEB subset hashes in [xrt-packages.json](../artifacts/xrt-packages.json) |
| `onnxruntime.tar.gz`, `deployment.tar.gz` | SDK 1.8.0 extracted distribution | Names/sizes recorded, full hashes deferred; archive-name similarity does not establish byte identity. C++ subset uses onnxruntime archive. |
| SDK `llvm_aie-1.8.0-...whl` | SDK distribution; specific Peano member recorded | Full hash deferred. This is distinct from IRON's LLVM-AIE 22 wheel. |
| `quicktest.tar.gz` / model | SDK distribution E059/E039 | Both hashed; model hash `7a78c7e85bac3a0681e3d2f77e69093a761e1c8f62f7fc65ff5ce3e1b82c5ba3` |
| ORT C API and EP C API headers | [ORT v1.27.0 source](https://github.com/microsoft/onnxruntime/tree/v1.27.0/include/onnxruntime/core/session) | Local Git blob IDs exactly match official files; SHA-256 in static-analysis.json. Headers not redistributed here. |
| MLIR-AIE source | [Xilinx/mlir-aie](https://github.com/Xilinx/mlir-aie), commit e28f6dc7e52fbb7b43f94b3693083c3f01a2387c | Source revision known; local env guard patch identified; do not rely on mutable latest-wheels channel |
| XRT validation support `xrt_smi_strx.a` | `https://raw.githubusercontent.com/Xilinx/VTD/2.21.75/archive/strx/xrt_smi_strx.a`, historical command in private history | E016 SHA-256 `57384f0d5cf3fc604b00540ed9b7542826cd961c30a2f3207357c972cc3ef32c` |

All listed hashes are observed identities, not vendor signatures or published security attestations. No archives, models, wheels or SDK binaries are tracked. A complete independently downloadable lockfile is not yet possible because wheel provenance and selected large hashes are missing.

## Astra R01/R03 supplement

The [historical input manifest](../artifacts/baselines/historical-cpp-sdk-1.8.0.json) retains null unknown hashes/member paths and blocks apply. A [separate new-acquisition template](../artifacts/baselines/new-acquisition.template.json) requires its own reviewed new-... ID; it cannot establish historical equality. See [baseline policy](baseline-policy.md).

[Host dependencies](host-dependencies.md) supplies actual SONAME→Ubuntu package/version mapping, cached acquisition metadata, conditional privileged install/delta instructions and a missing-dependency preflight. [The declared closure snapshot](../artifacts/cpp-static-preflight.json) covers 23 objects/109 edges without execution; actual loader/ABI and independent clean-host acceptance remain SKIP.
