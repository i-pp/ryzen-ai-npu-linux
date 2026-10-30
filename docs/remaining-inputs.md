# Remaining inputs: retained files, deferred hashes and unrecovered logs

**Investigation, recording and safe reproduction preparation are complete at this checkpoint; independent reproduction is unperformed. No historical input has been established as permanently lost.** The main SDK inputs are present, and a metadata-only follow-up located both IRON wheel candidates in pip HTTP cache. A subsequent authorized pass completed full current-file SHA-256 for the SDK outer archive, ORT, SDK Peano and both IRON wheels. Broader deferred hashes are not missing files. Exact acquisition/history and native acceptance remain distinct questions; see [completed hash pass](collected-input-hashes.md).

The [machine-readable follow-up](../artifacts/remaining-inputs-inventory.json) records presence, exact sizes, bounded search scopes, cache paths and small member hashes. The original metadata snapshot is retained with a later current-hash annotation. Exactly five complete container hashes now identify current bytes; historical successful-run equality remains unproven.

## Retained SDK inputs: no new download required

Paths use the repository's usual WORKSPACE/DOWNLOADS aliases. SDK rows below are relative to `<WORKSPACE>/ryzen-ai-1.8.0/` unless otherwise stated.

| File | Exact bytes | State / role |
|---|---:|---|
| `<DOWNLOADS>/ryzen_ai-1.8.0.tgz` | 7,819,506,855 | Present, full current SHA-256 complete in the selected pass. Historical linkage/member comparison unverified. |
| `onnxruntime.tar.gz` | 914,703,902 | Present, full current SHA-256 complete; frozen in a distinct current C++ baseline. |
| `llvm_aie-1.8.0-py3-none-linux_x86_64.whl` | 1,474,908,981 | Present, full current SHA-256 complete. SDK Peano21 member known; distinct from IRON LLVM-AIE22. |
| `deployment.tar.gz` | 914,704,018 | Present, full SHA-256 deferred. Broader SDK manifest; not required by this C++ subset helper. |
| `flexml-1.8.0-py3-none-linux_x86_64.whl` | 1,516,336,986 | Present, full SHA-256 deferred. Broader SDK distribution inventory. |
| `ryzenai_dynamic_dispatch-1.8.0-py3-none-linux_x86_64.whl` | 497,486,282 | Present, full SHA-256 deferred. Broader SDK inventory. |
| `vitis_aie_essentials-1.8.0-py3-none-linux_x86_64.whl` | 1,251,408,118 | Present, full SHA-256 deferred. Broader SDK inventory. |
| `voe-1.8.0-py3-none-linux_x86_64.whl` | 1,057,478,208 | Present, full SHA-256 deferred. ZIP metadata was inspected, not full payload hashing. |
| `cpp-test/peano/libpeano-lib.so` and `.so.21.0git` | 186,631,968 each | Both present as regular files; full hashes deferred. Do not assume duplicate bytes solely from sizes. |
| `quicktest.tar.gz` | 15,853,394 | Present and already hashed (E059); model separately pinned. No need to ask for it again. |
| `<DOWNLOADS>/RAI_1.8_Linux_NPU_XRT.zip` | 90,016,137 | Present and already hashed (E017); required DEB subset, including plugin, also hashed. |

Selected runtime ELF files above the earlier 64 MiB automatic hash cap also remain identified-but-unhashed in `static-analysis.json` (EP, Dynamic Dispatch, compiler, xcompiler and SDK Peano). They can be handled in a later sequential manifest pass. This is not a request to rediscover them or to hash the whole working environment.

The original installer exists locally as `install_ryzen_ai.sh` and its `install_ryzen_ai_py314.sh` variant, with known hashes/diff. Comparing the installer and selected inner archives to the **outer** SDK remains unperformed. A 10,240-byte compressed-header check found `.` then `./vitis_mllib-1.8.0-py3-none-linux_x86_64.whl` and stopped before that 9.6 MB payload. It did not enumerate later members or prove their exact outer paths. The later hash-only pass did not decompress/list members; a separate streaming member comparison remains unperformed. There is no evidence the member is absent.

## IRON wheel containers located

| Exact filename observed in cached HTTP metadata | Cached body size | Verified small metadata |
|---|---:|---|
| `mlir_aie-1.4.5.dev113+ge28f6dc-cp314-cp314-manylinux_2_35_x86_64.whl` | 265,463,510 | WHEEL and METADATA match the installed distribution byte-for-byte. |
| `llvm_aie-22.0.0.2026102001+4f5df13d-py3-none-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl` | 149,617,848 | WHEEL and METADATA match installed files; **filename is py3-none, internal WHEEL tags are cp310-cp310**. |

The `.body` locations are recorded precisely in the machine-readable inventory under `<HOME>/.cache/pip/http-v2/...`. They are ZIP wheel containers, not yet copied into a wheelhouse. At the metadata checkpoint only 306,325 bytes of central-directory/small metadata were read. The later selected pass fully hashed both raw containers without decompression, import, reinstall or native execution. Complete container hashes do not establish equality of all installed payloads. Cached HTTP metadata search read 361,432 bytes and extracted only relevant wheel filename tokens, without publishing headers or signed URLs.

Both installed dist-info directories retain INSTALLER=`pip`, REQUESTED and RECORD; neither has `direct_url.json`. That marker alone cannot recover the exact command. The official release-index URLs in the preserved env scripts remain source hints, not proof of the exact fetched asset URL.

The previous inference that normal pip selection necessarily requires a cp310 override is **superseded**. Read-only source inspection of preserved pip 26.2.2 shows candidate selection parses `Wheel(link.filename)`, while its unsupported-installed check reads internal WHEEL Tag metadata. This supports a normal filename-based selection followed by the observed platform warning. It does not prove the precise historical invocation or native/toolchain compatibility. The filename/metadata discrepancy must stay recorded; do not rewrite tags merely to silence a warning. See [PyPA wheel format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/) and [compatibility tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/).

## Search scope and limits

- Current metadata checks: exact SDK inputs above; SDK top level (34 entries), cpp-test depth 1 (15), MLIR top level (36), Downloads top level (11), 00_memcpy depth 2 (3), `/tmp` top level (1,719). Only relevant filename matches were retained.
- Pip `wheels/` directory was absent. Pip `http-v2/` metadata: 1,371 entries, non-body reads capped at 1 MiB (actual 361,432); this found the two candidates. UV `wheels-v7/`: 401 entries through depth 5, filenames/index metadata only, no matching package paths. An initial nonexistent `wheels-v5/` lookup is retained as history, not a whole-cache absence claim.
- Selected installed dist-info small files and three small pip source files were read. No SDK/AIE/pip module was imported/executed. No Codex/session history or unrelated home trees/external disks were searched. UV archive payloads and arbitrary/renamed wheel bodies remain outside this bounded search, but are not needed to rediscover the two now-located candidates.

## Logs: what the user need not resend

`/tmp/ryzenai-quicktest.log`, `/tmp/ryzenai-quicktest.strace`, `/tmp/ryzenai-xrt225.log` are retained and privately copied/hash-pinned (E096–E098). The parent collector already recovered historical user terminal output for memlock and the root/user 51.0 TOPS diagnostics. Missing separate local log files does not mean those observations are lost; prefer the collector's retained U bodies before asking the user again.

The memcpy result/DMA-warning attachment around **2026-10-30 10:23:51 UTC** remains unrecovered; its original filename is unknown. The visible U body is empty and attachment bytes/metadata were unavailable. 80.19 GB/s/1849 us remain A-level reading evidence. No matching standalone output was found in the bounded tmp/example searches. It may never have been redirected to a file; deletion/loss is not established. If the user still has that attachment or terminal capture, it is the main additional original log worth requesting.

Exact historical wheel-install/build commands or acquisition confirmations may also remain in the parent's already-collected U history/notes. This worker read its handoff rather than the entire raw export. Ask for user recollection/files only if that source does not answer the question. New runs cannot retroactively become original historical logs.

## Selected low-load hash pass — complete

The later authorized pass read exactly five retained files, totaling 10,624,201,096 bytes: two cached IRON wheels, ORT, SDK Peano and the SDK outer archive. Estimate recorded 15:30:13 UTC; start 15:31:44 UTC; finish 15:37:20 UTC; actual 335.811 seconds. Application maximum 32 MiB/s, buffer 1 MiB, one sequential worker, no download/extraction. All five before/after source identities and atimes matched. [Timing, controls, complete hashes and limits](collected-input-hashes.md).

A new current-input C++ baseline and separate IRON container record are frozen. Historical manifest nulls remain historical gaps, with explicit references to the now-computed current hashes. Vendor-published digests/signatures, exact acquisition receipt, outer-member comparisons and fresh native acceptance remain unverified. No current hash is promoted into contemporaneous historical evidence. Broader SDK/runtime files listed above were outside the selected five-file scope and remain deferred.

## Minimum independent verification scope and resources

- Prefer a separate idle EVO-X3 / Ryzen AI MAX+395-class NPU host with fresh Ubuntu 26.04 x86_64, or a separately booted test root/disk with preserved working roots unavailable. A container may test user-space staging/linking but shares the host kernel/driver and is not a full independent bring-up. No reboot/reinstall of the current successful root is proposed or authorized here; a second host avoids disrupting LLM work.
- Record hardware, actual kernel/amdxdna/firmware, ordinary-user device access and effective memlock. Match historical versions for an exact baseline or identify a new boot-tested host baseline. Helpers need Python>=3.12 and a C++17 compiler; the C++ branch does **not** require SDK Python3.12, the full SDK Python/LLM stack or GPU tests. Minimum RAM/CPU peaks were not measured; the vendor-style installer's 8 CPU/36 GB RAM/50 GB free checks are conservative planning references, not proven minima for this subset.
- First acceptance pass: reviewed pinned inputs → isolated staging → declared dependency preflight → new C++ link/load → one CPU and one VitisAI run using identical saved input/model → exit/actual selected libraries/NPU attribution → finite float32 [1,10] arrays and predeclared justified numeric comparison. Retain package before/after delta, cold-cache state, full logs, input/baseline hashes and residual warnings. The runners remain one attempt/180 seconds plus grace; no execution occurs in this follow-up.
- IRON compile/run with the now-located wheel candidates, and Python SDK validation if desired, are subsequent independent branches. GEMM throughput and memcpy bandwidth are not prerequisites for accepting the narrowly scoped C++ Run/numeric test, nor substitutes for it.

**User input in one batch:** if available, the original memcpy attachment/terminal output; any remembered acquisition URL/install command not answered by the parent's export; and the availability of a separate idle test environment/maintenance window. Existing SDK archives and the two wheel candidates do not need re-upload or re-download merely because their hashes were deferred.
