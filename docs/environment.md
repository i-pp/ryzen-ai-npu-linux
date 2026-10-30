# Observed environment and preservation boundary

This is a point-in-time record, not a supported-platform claim or an installation lockfile. Phase-1 capture was 2026-10-30 12:57:55 UTC; phase-2 supplements are separately timestamped.

| Layer | Observed configuration | Evidence and confidence |
|---|---|---|
| Hardware/OS | GMKtec EVO-X3, Ryzen AI MAX+ 395, Ubuntu 26.04.1, kernel 7.0.0-42-generic | Phase-1 DMI/CPU/OS/kernel probes, Verified |
| Kernel/NPU | PCI 1022:17f0, amdxdna in-tree; boot driver 0.7.0, firmware path `amdnpu/17f0_11/npu_7.sbin` | PCI/module/journal, Verified; FW 1.1.2.65 current symlink plus U historical report, Corroborated as loaded version |
| Permissions/limits | account database render/video; collector soft/hard memlock 1 GiB; PAM and systemd config 1 GiB | Saved config/process limits Verified; effective host device ACL/service limits unavailable to this namespace |
| System runtime | Ubuntu XRT 1:2.21.75+dfsg-4 | dpkg metadata and coreutil hash, Verified |
| MLIR-AIE/IRON | source e28f6dc7e52fbb7b43f94b3693083c3f01a2387c; Python 3.14.4; mlir-aie 1.4.5.dev113+ge28f6dc; LLVM-AIE 22.0.0.2026102001+4f5df13d | Source/config/metadata Verified; current cp310 LLVM-AIE tag on 3.14 remains an installation-compatibility gap |
| SDK Python | distribution 1.8.0; ryzenenv314 Python 3.14.4; ORT/VOE metadata 1.27.0/1.8.0 | Files/metadata Verified; successful Python execution is not evidenced |
| SDK C++ | ORT 1.27.0 C API, matched official headers, SDK Peano `libpeano-lib.so.21.0git` | ELF/hash/source and historical logs Verified |
| Local runtime | XRT base 2.25.37, XDNA plugin package 2.25, 24.04-amd64 package target | Version/package controls/hashes Verified; successful historical loader selection Verified |
| Host build tools | GCC/g++ 15.2.0, Clang 21.1.8, CMake 4.2.3, Ninja 1.13.2 | Version probes Verified; not all are necessary for the C++ probe |

Preserved inputs `<WORKSPACE>/ryzen-ai-1.8.0` and `<WORKSPACE>/mlir-aie` were read-only. The MLIR worktree already had modifications to `utils/env_install.sh` and `test/test_kernel_workflows.py`; neither was changed. No global Python, kernel, firmware, packages, shell startup files, live LLM/GPU services or system limits were altered.

New public code/docs are in this repository. Raw captures are under `.private-evidence/`; future isolated inputs/builds/runs belong under `.private-work/`. Both are gitignored. Do not commit SDK source copies, binaries, wheels, models, credentials, literal home paths, hostnames or raw conversation exports.

See [dependencies](dependencies.md) for required-versus-incidental packages, [the manifest](../artifacts/manifest.json) for machine-readable state, and [reproducibility status](reproducibility-status.md) for acceptance gates.
