# Phase 1 evidence index

Capture: 2026-10-30 12:57:55 UTC, with a small subsequent PAM/installer/hash supplement. This is current-state inspection plus preservation of historical evidence. No new NPU/GPU execution or vendor runtime import occurred.

`<WORKSPACE>` means the user-selected NPU workspace, `<HOME>` the user's home, and `<DOWNLOADS>` its download directory. Public records use these aliases. Original source paths and unredacted small source copies are restricted to the gitignored `.private-evidence/capture-20261030T125755Z/` directory, protected by directory mode 0700. The first capture `capture-20261030T125600Z` remains preserved too.

The [inventory](../artifacts/evidence-inventory.json) contains stable evidence IDs, source aliases, file sizes, source mtimes in UTC, SHA-256 when collected, and capture status. Mtime establishes file metadata, not when a command was executed. Symlink checksums refer to target bytes; symlink target names are recorded separately. Source files were read, not redistributed. Private `capture-file-checksums.json` hashes the collected files; it excludes itself.

## Findings and evidence

| Finding | Confidence | Source and scope |
|---|---|---|
| GMKtec EVO-X3, Ryzen AI MAX+ 395 | Verified | DMI vendor/product files, `cpu.json`; no serial numbers collected |
| Ubuntu 26.04.1, kernel 7.0.0-42-generic | Verified | `os.json`, `kernel.json` |
| NPU 1022:17f0 at 0000:67:00.1 uses amdxdna | Verified | `pci-npu.json`; `driver.json` identifies in-tree module |
| Boot journal reports driver 0.7.0 and loading `amdnpu/17f0_11/npu_7.sbin` | Verified | `kernel-npu-log.json` |
| Firmware version 1.1.2.65 was used at boot | Corroborated | Boot path plus current `npu_7.sbin.zst -> npu.sbin.1.1.2.65.zst`; no fresh device query |
| Collector process memlock is 1 GiB soft and hard | Verified | `process-limits.json`; describes this process only |
| PAM limit configuration is 1048576 KiB; user service drop-in is `LimitMEMLOCK=1G` | Verified | Source copies/hashes of `99-xrt-memlock.conf`, `user@.service.d/99-memlock.conf` |
| PAM login/sshd/sudo/su/gdm-password include pam_limits.so | Verified | Supplemental private `source-pam-*.txt` and inventory; common-session files alone do not establish every login path |
| Account database lists the user in render and video | Verified | `account-database.json`; effective host-session access remains Unknown |
| Host device ACL and active systemd service limits | Unknown | Device nodes are unavailable in this namespace; system/user bus reads returned Operation not permitted |
| System XRT packages 1:2.21.75+dfsg-4 remain installed | Verified | `packages.json`; source `libxrt_coreutil.so.2.21.75` hash |
| Local XRT is 2.25.37 from 24.04-targeted packages | Verified | Local `version.json`, package filenames, extracted library hashes; this does not imply general Ubuntu 26.04 support |
| MLIR-AIE revision e28f6dc7e52fbb7b43f94b3693083c3f01a2387c | Verified | `mlir-revision.json`, origin is Xilinx/mlir-aie |
| Existing MLIR checkout has two local modifications | Verified | `mlir-worktree.json`, `mlir-diff.json`: `utils/env_install.sh`, `test/test_kernel_workflows.py`; no edits made by this phase |
| Recorded MLIR submodules are uninitialized | Verified | Leading `-` for all five entries in `mlir-submodules.json`; not a source-build success claim |
| Both ironenv and ryzenenv314 use Python 3.14.4 | Verified | `pyvenv.cfg`, interpreter `-I -S -B --version` |
| NumPy 2.5.4 is installed in both environments | Verified | Distribution METADATA; does not prove it is required |
| mlir-aie 1.4.5.dev113+ge28f6dc and llvm-aie 22.0.0.2026102001+4f5df13d metadata exists | Verified | `packages-iron.json`; no wheel import or compiler execution performed |
| Python 3.12 was required by the vendor-style SDK installer | Verified | Existing `install_ryzen_ai.sh` has explicit 3.12 calls; original archive comparison still pending |
| Local SDK installer variant replaces four 3.12 references with 3.14 | Verified | `sdk-installer-diff.json`; two version calls, required minor version, venv creation call |
| Python 3.12 is absent everywhere on host | Unknown | It was not found on PATH, `/usr/bin`, dpkg, or bounded uv/opt paths; this is not a whole-host search |
| SDK venv contains ONNX Runtime 1.27.0 and VOE 1.8.0 metadata | Verified | `packages-sdk.json`; Python imports remain untested, cp312 extension files are present elsewhere in deployment |
| Historical compile-only failure occurred after EP registration/model compilation/session creation | Verified | Failure log lines 385–386, 740–752; [excerpts](evidence-excerpts.md) |
| Failing trace opened system libxrt_coreutil.so.2 | Verified | strace line 49 returns file descriptor 3; proves an open, not ABI compatibility or completed initialization |
| Successful log loads local XRT and ends in Inference/Quicktest PASS | Verified | Success log lines 387, 1151, 1154, 1227–1234; log content verified, no re-execution |
| 398 NPU operators, 2 VITIS_EP_CPU operators, one NPU subgraph reported as actually running | Verified | Success log lines 793–799; counts are not utilization or timing fractions |
| Runtime selection caused the observed change | Corroborated | Consistent failed/success logs plus unchanged working launcher; simultaneous variable/library changes have not been independently isolated |
| Exact XRT symbol/ABI mismatch is the sole root cause | Inferred | No symbol-level proof or controlled A/B run; success log also contains optional-symbol lookup errors at 410–412 |
| Historical quicktest validated numerical output | Unverified | C++ source only checks API return status/output count, then prints output name; it does not compare values |
| XRT 51 TOPS, IRON 80.19 GB/s, 1849 us, PASS and DMA reuse warnings | Unverified | Instruction-sheet leads; no original local output recovered in this phase |
| Clean-room reproducibility | Unknown | Not attempted |

## Retained source artifacts

The inventory includes SDK installer files/activation patches, required SDK archive metadata, local XRT .deb packages/version/libraries, system XRT library, ONNX Runtime library, Peano metadata, quicktest source/executable/model, MLIR environment scripts/example sources, relevant host configuration, firmware, and the three historical runtime logs. SDK source copies and configuration are private, not licensed for redistribution by this repository.

Relevant APT/dpkg excerpts and 43 selected shell-history lines are private. The shell history has no timestamps; command presence is not proof of success. No complete shell history, generic environment dump, credentials, serial numbers, or Codex session data was collected.

[Representative sanitized logs](evidence-excerpts.md) retain original line numbers. The two historical runtime log hashes and strace hash are in the inventory and source hash manifest.

The 90 MB XRT ZIP received a targeted streaming SHA-256. The 7.8 GB SDK download and remaining artifacts over the collector's automatic 64 MiB cap are explicitly marked deferred; no whole-disk hashing occurred. The cap does not itself determine whether an artifact is required for later reproducibility.

## Phase-2 additions

- [Static analysis](../artifacts/static-analysis.json): selected ELF dependencies/SONAME/RPATH, XRT-namespace import-name comparison, official-matched header hashes and static model metadata. Reproducible through `scripts/analyze-runtime.py`; no dynamic loading or SDK import.
- [Phase-2 supplement](../artifacts/phase2-evidence.json): WHEEL/dependency metadata, cp314 pyxrt link, exact upstream env-script hash, XRT controls/payload mapping and original/current SDK Python ELF evidence. The CPython ABI and LLVM-AIE platform gaps remain explicit.
- [XRT package input pins](../artifacts/xrt-packages.json): required local user-space extraction subset, including targeted plugin hash `ac47b5c731931dec16d5673a64cc308ebd07f7637c8f34bba89167d63980576a` for 69711164 bytes. This is an observed local identity, not a vendor signature.
- [Conversation handoff](conversation-evidence.md): source-linked U/A/I summaries from the parent's collector. Original raw history/attachments were not available to this worker. It corroborates the memlock sequence, XRT diagnostic results and actual C++ bypass, while retaining omissions.
- [Causal analysis](xrt-investigation.md), [chronology](chronology.md), [completeness audit](completeness-audit.md), [verification design](verification-design.md) and [phase-2 checkpoint](phase2-checkpoint.md) separate facts, reconstructed commands, fixture tests and unperformed clean-host integration.

The phase-1 evidence rows above retain their capture-time confidence. Newly recovered context is explicitly additive; in particular, “51 TOPS unverified” there meant no local original log in phase 1, whereas the parent has now recovered historical U output. No current hardware benchmark is implied.
