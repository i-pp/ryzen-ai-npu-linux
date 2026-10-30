# Reproducibility status

**Historical C++ API success is evidenced. Independent clean-install reproduction and numerical model correctness remain unestablished.** Investigation, recording and safe reproduction preparation have a reviewable completed checkpoint; the Japanese draft/Astra review exist. Retained inputs and missing historical logs are classified in [remaining inputs](remaining-inputs.md). The [selected five-input hash pass](collected-input-hashes.md) is complete for a new current-input baseline.

| Claim | Status | Practical limit |
|---|---|---|
| Original successful C++ runtime configuration exists | Verified current source + historical log | Original environment never rerun here; exact original full build command/cache context incomplete |
| Local XRT selection enabled observed completion | Corroborated | Multiple runtime-selection factors changed; exact internal ABI/initialization branch not isolated |
| Hardware/driver/firmware worked historically | Corroborated by local/boot/U evidence | Device/ACL hidden in current namespace; no fresh test |
| XRT GEMM 51.0 TOPS | Historical U log recovered through parent collector | Root and user contexts differ; raw local file/config missing; not ONNX throughput |
| IRON samples worked | SAXPY/reduce U PASS; memcpy A-level report | Original memcpy attachment/warnings not recovered; no new run |
| SDK Python 3.12 worked | Unknown / not evidenced | Current venv3.14; 3.12 absent from bounded probes; no successful provisioning log |
| SDK Python 3.14 worked | Contradicted by historical import failures | execstack edit did not resolve ABI; metadata installation is not import success |
| Matching MLIR/LLVM wheel reinstall can be repeated | Inputs located; fresh reinstall unperformed | Both cached ZIP containers now have full hashes in a frozen current-input record and match selected installed WHEEL/METADATA only; historical source attestation and native acceptance remain pending. LLVM-AIE py3-none filename/internal cp310 mismatch is a packaging warning, not proof that forcing was needed. |
| New verification tooling behaves on fixtures | Tested offline | Does not imply vendor loading, staging integration or hardware execution |
| Actual ONNX outputs match a reference | SKIP | Historical source lacks comparison; new probe/comparator unexecuted on real SDK/model |
| Clean installation reproduces all layers | NOT PERFORMED | Required artifacts, compatibility and independent integration acceptance outstanding |

## Outstanding gates

1. **Input provenance/integrity:** all key SDK distributions are present. Full current hashes are now complete for SDK outer/ORT/SDK Peano and two IRON wheels; broader inventory hashing remains deferred. Historical acquisition linkage and selected outer-member comparison remain unverified. XRT subset/model/header pins already exist. [Exact files, sizes and plan](remaining-inputs.md).
2. **IRON installation:** two original-name wheel candidates have now been found in pip HTTP cache and match installed WHEEL/METADATA. Full container hashes are now complete; historical source attestation, full installed-payload equivalence and independent native acceptance remain. The filename/internal-tag discrepancy explains a plausible normal-selection/later-warning path; neither forced installation nor permanent loss is established.
3. **Historical metrics/warnings:** obtain actual memcpy attachment/log and exact DMA diagnostic/target/cache configuration. A-level readings remain labelled. The new original-model metadata does not recover missing historical output values.
4. **Host acceptance:** capture effective device permissions and relevant user-manager/service limits from an authorized host shell. Current namespace denials are not failed host configuration. No bypass or escalation was attempted.
5. **Independent clean host:** stage verified inputs, link/load the new probe, exercise IRON and ONNX under explicit authorization, capture exit/selected libraries/device evidence and compare real outputs with justified tolerances. Record any unsupported-package/OS boundary.
6. **Rights/export:** the Japanese draft, Astra review and targeted repairs now exist. License, third-party provenance, approved export/history and public destination/link review remain. No extra Astra run, remote, push or publication is authorized/performed by this follow-up.

The absence of a decisive XRT ABI explanation is an explanatory limitation, not a reason to stop independent documentation or tooling work. The unverified historical linkage/native compatibility and unperformed clean-host execution remain blockers to claiming a reproduced installation; the two cached wheel containers themselves are now located and hashed. See [completeness audit](completeness-audit.md) and [phase-2 checkpoint](phase2-checkpoint.md) for ownership and validation evidence.

## Astra follow-up status

The historical input BLOCKER remains. A manifest-driven new-acquisition branch now has a distinct ID and explicitly disclaims historical equality; [baseline policy](baseline-policy.md) defines both modes. [Host prerequisites/preflight](host-dependencies.md) now map actual SONAME/package/version ownership and stop on missing dependencies. Build/result no-replace safety repairs have device-free fixtures. None of these changes is independent clean-host acceptance. The writer subsequently removed its remaining private identifier, so the current-tree locator scan passes. Native history and rights/export remain separate [publication gates](publication-gates.md). [Repair evidence](reviews/astra-remediation.md) is separate from the original audit.

## Retained-input clarification after the repair snapshot

The original R01 completion blocker is an unfinished input-pinning/acceptance gate, not proof that historical restoration is impossible. SDK archives and the two IRON wheel containers are locally present. Full hashing of the five selected containers is now complete without re-download; selected archive-member comparison remains unperformed. The writer subsequently repaired its private-identifier/old-CLI references; native Git history, rights/export and independent clean-host gates remain separate. The [bounded follow-up](remaining-inputs.md) supersedes older statements that wheel containers had not been located.

## Current collected-input checkpoint

[Five full hashes](collected-input-hashes.md) remove the selected current-file integrity gap. The [new C++ baseline](../artifacts/baselines/new-collected-cpp-sdk-1.8.0-20261030.json) is separately named and the existing helper accepts its plan-only manifest contract. This does not clear historical equivalence/vendor authenticity or independent staging/link/load/Run/numeric acceptance. No original environment or article was modified.
