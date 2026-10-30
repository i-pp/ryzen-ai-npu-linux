# C++ host prerequisites and static dependency gate

Astra R03 identified that extracting SDK/XRT files does not install host dependencies. The [host inventory](../artifacts/host-dependencies.json) now records SONAME providers, actual Ubuntu package/version ownership, configured public APT repositories and cached archive filenames/SHA-256. This is local dpkg/APT-cache evidence, **not fresh archive retrieval or clean-host validation**.

| SONAME | Provider in the candidate graph | Observed host package/version |
|---|---|---|
| `libc.so.6`, `libm.so.6`, `ld-linux-x86-64.so.2` | host | libc6 2.43-2ubuntu2.4 |
| `libgcc_s.so.1` | host | libgcc-s1 16-20260322-1ubuntu1 |
| `libuuid.so.1` | host | libuuid1 2.41.3-3ubuntu2.2 |
| `libzstd.so.1` | host | libzstd1 1.5.7+dfsg-3 |
| `libncurses.so.6`, `libtinfo.so.6` | host | libncurses6/libtinfo6 6.6+20251231-1 |
| `libstdc++.so.6` | SDK-bundled selected copy | Host libstdc++6 16-20260322-1ubuntu1 is installed/needed by host tools; it is not this graph's selected runtime copy. |
| `libz.so.1` | SDK-bundled selected copy | Host zlib1g 1:1.3.dfsg+really1.3.1-1ubuntu3.2 is installed; a fallback/other-tool dependency here. |
| ORT/compiler/Peano/XRT names | staged vendor subset | No host package is substituted for these archive pins. |

The [static preflight snapshot](../artifacts/cpp-static-preflight.json) traversed **23 objects / 109 DT_NEEDED edges** from explicit ORT, EP, SDK Peano and local coreutil/core/XDNA-plugin roots without loading them. All declared dependencies resolved within candidate inputs and standard host paths. Recheck a different/new archive baseline.

## Conditional privileged provisioning on an independent clean host

Record a private clean-host package inventory and APT source definitions first. On that future host only, an authorized administrator may update indices, inspect a simulated transaction and approve the package delta. No command below was executed here. See [Ubuntu package-management guidance](https://documentation.ubuntu.com/server/how-to/software/package-management/).

```bash
dpkg-query -W -f='${binary:Package}\t${Version}\t${Architecture}\n' > packages-before.tsv
sudo apt-get update
apt-get --simulate install --no-install-recommends \
  bash coreutils python3 binutils dpkg g++ libc6-dev \
  libc6 libgcc-s1 libuuid1 libzstd1 libncurses6 libtinfo6
```

After reviewing the delta and recording the chosen baseline's versions/acquisition, the corresponding install is:

```bash
sudo apt-get install --no-install-recommends \
  bash coreutils python3 binutils dpkg g++ libc6-dev \
  libc6 libgcc-s1 libuuid1 libzstd1 libncurses6 libtinfo6
dpkg-query -W -f='${binary:Package}\t${Version}\t${Architecture}\n' > packages-after.tsv
```

Use the future private run directory for those files. Python must be >=3.12 and the compiler C++17-capable. APT resolves g++/binutils dependencies. Observed g++-15 is 15.2.0-16ubuntu1, while the g++ metapackage is 4:15.2.0-5ubuntu1; the build receipt records the actual compiler realpath/hash/version. Do not indiscriminately install all SDK DEB dependencies such as DKMS, Boost, OpenCL, CUDA or SDK Python packages.

If preflight discovers another missing SONAME, stop and identify its Ubuntu owner/source/version before adding it to the reviewed delta. `zlib1g` is the named fallback for host `libz.so.1`; changing to a fallback is a new selection, not an exact historical match.

Use recorded `package=version` pins only after confirming exact archives and the full dependency transaction are available. Do not force current-host downgrades. The inventory includes a locally customized coreutils label; it is not assumed publicly retrievable or required. A fresh supported package set is a **new host baseline** by default.

## Kernel and firmware

The module is owned by `linux-modules-7.0.0-42-generic` (7.0.0-42.42); its image package is `linux-image-7.0.0-42-generic` (7.0.0-42.42). The NPU firmware file is owned by `linux-firmware-amd-misc` (20260319.git217ca6e4-0ubuntu1.1). Cached archive names/hashes are in the inventory where available; fresh archival retrieval/boot were not tested. A generic firmware metapackage alone does not identify the loaded bytes.

A future kernel/firmware choice must match recovered historical artifacts or be boot-tested as a distinct baseline. No helper changes these packages. Reboot only on the future host when changed kernel/firmware must be loaded, then capture PCI/boot/driver evidence.

## Preflight before linking/loading

```bash
python3 -I -B scripts/preflight-cpp.py --sdk-root "$NPU_CPP_ROOT" --xrt-root "$NPU_XRT_ROOT"
```

Unresolved SONAMEs, out-of-candidate dependencies, unreadable ELF objects and unowned host libraries give FAIL/exit 1. Complete declared resolution gives `static_status=PASS` but aggregate SKIP/exit 2: ABI, symbol versions, conditional dlopen targets, actual process selection and driver initialization still need an authorized fresh process. No ldd, loader, compiler, SDK code or device is run by this helper. Missing-SONAME and preserved-environment-leakage fixtures cannot pass it.
