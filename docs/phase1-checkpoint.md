# Phase 1 handoff

Useful results are in the manifest and evidence index. The strongest historical evidence is the preserved failing C++ log/strace and successful loader/inference log. Both original working environments were treated as read-only.

## Completed

- Read all 936 lines of the instruction sheet through Library. Its Library filename is `貼り付けたテキスト(5).txt`, content heading is “Ryzen AI NPU on Ubuntu 26.04 — Complete Bring-up Reconstruction and Reproducibility”, ID `REQ-001`, source size 25553 bytes. Full content was read in three explicit windows (1–320, 321–640, 641–936); no instruction-sheet text is redistributed here.
- Read global `AGENTS.md`; no NPU-workspace-specific AGENTS file was found. The separately inspected Project-KISS AGENTS applies to that repository and was not treated as permission to change it. `docs/ai/orchestration.md` is unresolved.
- Initialized Git only in the new project directory. No remote, push, publish, global configuration, installation, rebuild, or device execution.
- Collected host identity, OS/kernel, PCI/driver/firmware evidence, selected packages/toolchains, source configuration, process memlock, XRT package/runtime metadata, venv/interpreter/distribution metadata, SDK/model/application provenance, MLIR revision/local diff/submodule state, historical runtime logs, selected apt/dpkg/shell history.
- Preserved original logs privately, created sanitized representative excerpts and source SHA-256 records, recorded gaps and namespace restrictions.
- Added `scripts/inspect-environment.sh` and `scripts/collect-evidence.py`. They collect metadata and report unavailable probes; they are not inference/compatibility tests. Bash/Python syntax and an actual read-only collection were checked.

## File boundary for following workers

Phase 1 owns `.gitignore`, `README.md` checkpoint, `artifacts/manifest.json`, `artifacts/evidence-inventory.json`, `artifacts/SHA256SUMS`, `docs/evidence-index.md`, `docs/evidence-excerpts.md`, `docs/chronology-evidence.md`, `docs/missing-evidence.md`, this checkpoint, and the two inspection scripts. `.private-evidence/` contains the original snapshots and supporting one-off collection; never stage it.

The analysis/script worker can extend the manifest with explicit evidence references, derive reproduction commands, implement separate verification/execution scripts, and explain the XRT mechanism. Preserve the distinction between API PASS, device execution reported by the runtime, numerical validation, and clean-room reproducibility. In particular, treat `quicktest.cpp` as C API use from C++; it is not a numeric regression oracle.

The documentation worker can use the chronological scaffold, write the required component documents and completeness audit, then draft the Japanese article. Recover missing conversation evidence before making the 51 TOPS/IRON metrics public facts. A source file or command proposal cannot substitute for an executed test log.

The independent final auditor should test whether a clean machine can obtain all pinned artifacts and prerequisites, inspect source-build versus wheel-install claims, challenge the unresolved Python 3.12/3.14 story and exact ABI explanation, and require explicit numeric correctness criteria. Clean-room reconstruction remains unperformed.

## Private lookup

Canonical capture for this checkpoint: `.private-evidence/capture-20261030T125755Z/`. The private inventory maps original paths to `source-NNNN.txt` copies. The three diagnostic logs also have their original basenames in the earlier capture `capture-20261030T125600Z/`; the canonical capture's source-copy filenames are mapped in its inventory. `shell-history-selected.json` contains only the 43 relevant, secret-filtered history entries and has no timestamps. `capture-file-checksums.json` covers private capture files except itself.

The private helper `build-phase1-records.py` generated the initial public records; it is scratch implementation, not an installation script or a public contract. Future changes to records should be reviewed as ordinary evidence edits, not blindly regenerated from stale scratch assumptions.

## Verification limits

No prior successful environment was re-executed, reinstalled, cleaned, or rebuilt. Interpreter version probes use `-I -S -B --version`; no SDK/AIE imports were run. Device nodes are hidden/unavailable to this namespace and bus queries were denied. Current-state hashes provide point-in-time identities, not proof that every byte of both large environments is unchanged. Existing MLIR local changes were present before this phase and remain preserved.

No license grant for the newly authored repository has been selected; SDK artifacts are not included. Publication and final editorial review remain separate.

## Recorded validation outcome

2026-10-30 phase-1 validation: 45 preserved source-copy hashes matched the canonical source inventory; 16 selected pre-existing SDK/MLIR source/configuration artifacts matched their first-capture hashes. JSON parsed, Bash/Python syntax passed, public records contained no literal personal home path/hostname, and relative Markdown links resolved. The collector completed with six unavailable/partial probes: Python 3.12 lookup, wildcard package query, device-node query, device ACL query, systemd user-manager query, and systemd user-service query. These are inspection outcomes, not compatibility or execution test results. Final validation used saved evidence without rerunning unavailable probes.
