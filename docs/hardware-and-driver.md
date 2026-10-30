# Hardware, kernel and firmware

**Verified current state:** EVO-X3/MAX+395; PCI `1022:17f0` at `0000:67:00.1`; amdxdna bound and available in-tree for kernel 7.0.0-42-generic. Boot journal reports driver 0.7.0 and loading `amdnpu/17f0_11/npu_7.sbin`. On disk, `npu_7.sbin.zst` points to `npu.sbin.1.1.2.65.zst` (E089/E091). The kernel path and current symlink plus conversation FW report corroborate the version; no fresh firmware/device query occurred.

The original conversation initially shows kernel 7.0.0-38, then 7.0.0-42. Its update/reboot commands and exact timing are not recovered. Do not imply that upgrading from 38 to 42 was isolated as necessary for inference. The observed setup is not a general Ubuntu 26.04 compatibility guarantee; the SDK packages are labelled for 24.04.

**Diagnostic, read-only commands for a clean host:**

```bash
uname -r
lspci -nnk -d 1022:17f0
modinfo amdxdna
readlink /lib/firmware/amdnpu/17f0_11/npu_7.sbin.zst
journalctl -k --no-pager -g 'amdxdna|amdnpu' -n 100
```

Success requires a matching PCI function bound to amdxdna and a boot log with successful firmware initialization. A firmware file alone proves availability, not that it is loaded. A missing node or denied journal in a container/agent namespace is **SKIP**, with a host-shell follow-up, rather than proof that the physical host lacks an NPU.

**Conditional, privileged, isolated clean host only:** install the appropriate Ubuntu kernel/firmware package if actual host inspection shows it is absent or unsupported. Exact archived 7.0.0-42 package acquisition is not preserved, so no invented APT pin is given. Reboot only if a different kernel/firmware must actually be loaded, then inspect the new boot. Do not install SDK DKMS packages over a working in-tree module during reconstruction.

Astra follow-up records the exact observed image/module package names, firmware owner, cached archive identities and the distinction between historical pins and a new boot-tested baseline in [host dependencies](host-dependencies.md). Those package files have not been freshly retrieved or boot-tested by this project.
