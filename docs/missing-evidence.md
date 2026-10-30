# Missing evidence and access limits

Current clarification: [retained input inventory](remaining-inputs.md) distinguishes present SDK files, now-located cached IRON wheels, and unrecovered original logs. [Five selected container hashes](collected-input-hashes.md) are now complete; broader hashes remain deferred. None is declared permanently lost. These follow-ups supersede older hash/wheel-location statements below.

## Phase-2 update (supersedes affected phase-1 rows below)

- Parent collector recovered visible conversation U logs for the 64 MiB/-11 memory failure, later process/service limits, root/user XRT validation (51.0 TOPS), SDK Python execstack/ABI failures, C++/Peano work and local-XRT success. Phase 2 received the source-linked handoff, not raw JSON/omitted attachments; see [conversation provenance](conversation-evidence.md).
- Current targeted inspection confirms a cp314 pyxrt symlink inside ironenv, and the incorrect systemd drop-in path is absent now. The historical exact link/removal commands and times remain Unknown.
- Original memcpy attachment and exact DMA warning remain unavailable. 80.19 GB/s/1849 us are still A-level assistant readings, not recovered raw results.
- Official ORT v1.27.0 header blob identities match local bytes. Static model IO shape and bounded XRT import-name coverage are now recorded. This does not establish numerical correctness or a unique ABI root cause.
- The XRT plugin DEB has a targeted SHA-256; SDK distribution/ORT archive/SDK Peano and both IRON container current hashes are now complete. Original vendor installer/outer archive-member comparisons remain pending.
- IRON native acceptance gap: installed LLVM-AIE 22 WHEEL has cp310 tags although ironenv is cp314. The now-located container filename is py3-none, which supports normal filename selection followed by an internal-tag warning. Historical acquisition/method and fresh native compatibility remain unverified.
- Canonical `i-pp/ai-orchestration` policy and referenced permission/role files were retrieved; [policy provenance](policy-provenance.md) resolves the earlier lookup gap.
- New C++ output probe and numeric comparator are implemented; syntax/fixture checks do not replace a real same-input CPU/NPU comparison. No new device test or clean install occurred.

The following table is the retained **phase-1 checkpoint**, not a statement that these newly resolved items are still wholly unavailable. Current acceptance blockers are in [reproducibility status](reproducibility-status.md).

## Phase-1 checkpoint

| Item | Status | Exact action/target and reason | Next safe step |
|---|---|---|---|
| Effective device permissions / ACL | Unavailable in this execution namespace | `ls -ld /dev/accel /dev/accel/accel0 /dev/dri` reports missing paths; `getfacl /dev/accel/accel0` likewise cannot inspect it | Human host-shell read-only capture if required; do not infer physical absence |
| Effective systemd user-manager / user service limit | Denied by execution environment | `systemctl --user show --property=DefaultLimitMEMLOCK` and `systemctl show user@1000.service ...` returned Operation not permitted on their buses | Keep present config and process limits; obtain host-shell output later, no configuration change |
| Historical 8 MiB limit / 64 MiB failure | Unverified | No original failure output recovered; selected untimed shell history only records attempts | Recover conversation output/attached log; do not manufacture errno or a required logout |
| XRT validation 51 TOPS | Unverified | Original validation output not found in selected local evidence; support archive is present | Recover original test name/configuration and output through conversation/attachments |
| IRON PASS / 80.19 GB/s / 1849 us / DMA warnings | Unverified | `00_memcpy` source exists; no corresponding original benchmark output/build log recovered | Obtain original output and input/configuration; analyze warnings before asserting harmlessness |
| Python 3.12 provisioning | Unknown historical step | No PATH, /usr/bin, dpkg, bounded uv/opt interpreter found; both existing venvs report 3.14.4 | Reconcile instruction-sheet assumption with conversation and any missing environment; do not install during reconstruction |
| SDK Python import compatibility | Not tested | Metadata is present; cp312 deployment extension filenames exist alongside a 3.14 venv | Separate later import tests from C++ runtime proof; do not assume broad Python 3.14 support |
| Original vendor installer comparison | Pending | Local original-named script and py314 variant captured, their difference known; archive original not extracted/read | Compare only the necessary member using a bounded archive read; no reinstall |
| SDK archive provenance / EULA | Unknown | Archive names/sizes/hashes are partial evidence; no authenticated acquisition receipt or license acceptance output recovered | Record official source and manual/authenticated requirements from allowed references |
| Large archive hashes | Deferred | 7.8 GB SDK and other large artifacts intentionally not streamed under this phase's I/O budget | Targeted later hashing if needed; not full-disk hashing |
| Exact C++ compiler/link command | Unknown historical command | Executable RUNPATH and source exist; no historical build command captured | Derive a clearly labelled reconstruction command in the later scripting phase |
| Model output shape and numerical validity | Unknown / not implemented | Historical C++ source does not query output dimensions or compare values | Static model inspection plus a later independent numerical oracle |
| XRT symbol/ABI root cause | Inferred | Failed trace proves open of system library; successful log proves local init and PASS; it does not identify failing symbol/initialization branch | Analyze static dependencies/symbols, preserving alternative explanations |
| Full conversation | Unavailable to this worker, parent ingestion pending | Shared URL opened with no readable lines. `global_search.read_conversation_context` is absent from available tools, including after tool discovery. Parent supplied formal conversation ID `HIST-CONV` | Parent can provide authorized conversation excerpts with timestamps; keep proposals distinct from executed commands |
| Codex session history | Not accessed | Session areas excluded by task restrictions | Use permitted exported evidence only |
| Git canonical `docs/ai/orchestration.md` | Not found in inspected known locations | No such file in NPU workspace, inspected home/global locations, or Project-KISS tracked paths | Parent to identify its canonical repository/path; do not fabricate it |
| Independent clean-room test | Not performed | This phase is explicitly read-only and preserves the successful environment | Separate isolated clean-install validation and final independent audit |

No automatic-approval rejection occurred. The service bus denial is an execution-environment restriction, not a failed system configuration. No escalation, sudo invocation, device test, or alternate access path was used to bypass it. Package-query output is partial because wildcard matches for xdna/Python 3.12 were absent; that nonzero exit does not discard the installed XRT/Python 3.14 records.
