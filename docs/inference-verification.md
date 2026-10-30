# Inference and numerical verification

The strongest preserved result is E098: ORT 1.27.0, EP registration, session creation, inference and quicktest PASS, with 398 NPU operators, 2 VITIS_EP_CPU operators and one reported NPU subgraph. This is Verified historical log content. Those reports are not an independent hardware execution trace, timing/utilization shares or numerical validation.

| Level | Acceptance evidence | Current status |
|---|---|---|
| Environment detected | PCI/driver/configuration visible | Captured; host device ACL/service effective state partly unavailable in this namespace |
| Dependencies compatible | Correct interpreter/native imports and complete selected runtime closure | C++ historical completion; SDK Python 3.14 failed; LLVM-AIE tag warning remains |
| Compilation successful | Session/compile result plus retained artifacts/configuration | Historical model compilation/partition output; not a new clean compile |
| Device execution successful | Actual Run completes, exit=0, runtime NPU attribution and selected libraries | Historical E098 reports completion; original process exit code not separately captured, fresh test SKIP |
| Numerical output validated | Same model/input bytes, correct shape/type, finite values, justified CPU/NPU comparison | Historical SKIP; new probe/comparator implemented and fixture-tested, real arrays unavailable |
| Clean-install reproducible | Independent host can obtain pinned inputs and pass all required stages | Not performed; several input/compatibility gates unresolved |

## Saved evidence

```bash
bash scripts/verify-inference.sh --log <saved-success-log>
bash scripts/verify-inference.sh --log <saved-failure-log>
```

The success log's API/NPU-report subchecks pass, but overall SKIP remains for fresh execution, exit status and numerical validation. The failed compile-only log returns FAIL. The verifier does not treat “No driver detection supported” or every LD_DEBUG symbol-lookup diagnostic as a fatal result: they also occur in success evidence. A partition/“Actually running” line without a completed Run is insufficient.

For a future run's split logs, provide `--log <stdout> --stderr-log <stderr> --run-result <result.json>`. Retain both originals and their exit metadata; concatenated streams do not establish precise event ordering. The verifier only evaluates supplied saved evidence and never starts the application.

## New comparison contract

The new CPU/VitisAI probe records `model_sha256`, `input_sha256`, `onnxruntime_version`, `provider`, and ordered outputs `{name, shape, dtype, values}`. `run-npu.sh` checks file hashes before launching and captures completion hashes and process information privately. `verify.py compare` requires CPU and VitisAI records for ORT 1.27.0, matching SHA-256 identities, matching names/types/shapes/element counts, nonempty output lists, finite float32 values and explicit nonnegative finite tolerances.

For every value, the criterion is `abs(npu-cpu) <= atol + rtol*abs(cpu)`. It reports mismatch count and maximum absolute error. Example diagnostic command:

```bash
python3 -I -B scripts/verify.py compare --reference <cpu.json> --candidate <npu.json> --atol 0 --rtol 0
```

Zero tolerance is an exact diagnostic, not an established acceptable error bound for this quantized model. Choose and document model-appropriate tolerances **before** collecting results; do not relax them simply until a test passes. The comparator deliberately supplies no silent default.

The CPU reference uses the same vendor ORT with no VitisAI registration; this detects differences between those execution paths. It is not an independent mathematical oracle or an accuracy evaluation against labelled data. For stronger assurance, add a separately validated reference implementation/test set, boundary/adversarial inputs and repeated independent runs. No such result is claimed here.

Astra follow-up: output publication is now exclusive/no-replace after complete writing, so a failed or losing concurrent writer cannot overwrite an old record. Temporary files are not completed results. Runner metadata retains the staging baseline ID/kind when available; a new-acquisition baseline never proves historical archive equality. See [baseline policy](baseline-policy.md) and [remediation](reviews/astra-remediation.md).
