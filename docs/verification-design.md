# Verification contract and execution boundary

All `verify-*.sh` wrappers use the Python standard library and selected metadata commands. They never import SDK/AIE modules, open the accelerator, install packages or compile existing code. Their default mode has no device execution. `inspect-environment.sh` remains a collector, not a compatibility test.

| Entry point | Offline/read-only work | Execution boundary / missing evidence |
|---|---|---|
| `verify-environment.sh` | PCI binding, effective node access without opening, current process memlock, package/module/file metadata | Loaded firmware, host ACL where hidden and service bus values SKIP; no xrt-smi |
| `verify-mlir-aie.sh --mlir-root DIR` | exact source revision, changed-file count, recorded venv/package layout/version | no import/compiler/device claim; wheel tags/platform warning must be reviewed |
| `verify-iron.sh --log FILE` | PASS/failure markers, DMA warning count in supplied log | without log SKIP; no device/cache mutation; a PASS marker alone lacks exit/config/output evidence |
| `verify-inference.sh --log FILE` | ORT/EP/session/Run/quicktest stages, compile-only veto, reported NPU subgraphs, diagnostic retention | no numerical check from historical quicktest; optional split stderr/result metadata; no actual runtime launch |
| `verify.py model --model FILE` | bounded top-level ONNX protobuf metadata and hash | no checker, shape inference, external-data validation or execution |
| `verify.py compare ... --atol A --rtol R` | supplied CPU/NPU provenance/shape/finiteness/values | provided-array result only; run provenance and model accuracy require separate evidence |
| `analyze-runtime.py --sdk-root DIR` | ELF graph/SONAME/RPATH, selected hash identities, bounded XRT import-name comparison | no ldd/dlopen; no symbol-version/C++ semantic/driver compatibility guarantee |

Each verifier prints JSON. **PASS** means that specific check met its stated criterion. **FAIL** means a supplied test/artifact contradicts that criterion. **SKIP** means the required evidence/capability was absent or that execution was deliberately not performed. Aggregate returns: `0=all PASS`, `1=at least one FAIL`, `2=no FAIL but at least one SKIP`. A namespace-hidden node is SKIP; a visible node without current read/write access is FAIL for this process's access check, not proof of failed hardware.

The inferred minimum memlock was not measured. The environment verifier compares against this snapshot's chosen 1 GiB and labels that scope. Package/file presence is an inventory result; compatible native execution is separate. No single aggregate PASS can be used to imply a clean install unless the separate clean-install acceptance record exists.

## Mutating helpers, all opt-in

- `stage-xrt.py`: dry plan by default; `--apply` extracts only verified user-space payload into a new `.private-work` tree. No dpkg installation, maintainer scripts, kernel or firmware changes. Existing receipt/content mismatch stops without overwrite; interrupted partials are retained for inspection.
- `stage-cpp-sdk.py`: dry plan; apply requires explicit archive hashes and license acknowledgement. Only isolated C++ subset, headers, SDK Peano and model. No full vendor install/Python/ELF patch. Whole-input archival hashes remain prerequisites.
- `patch-iron-python.py`: dry plan; exact before/after file hashes and isolated path guard. Changes acceptance guard only, not ABI.
- `build-probe.py`: dry plan; apply compiles only newly authored source in an isolated C++ SDK. No vendor runtime execution; mismatched existing build is preserved.
- Astra repair: outputs use no-follow leaf checks and an exclusive build lock; compiler output is private, then app/receipt publish without replacement. Dangling symlinks/unowned outputs fail before compiler startup. The same absolute compiler/path/hash/environment supplies version and build evidence.
- `make-input.py`: dry plan; apply creates deterministic serialized input idempotently inside `.private-work`.
- `run-npu.sh` and `run-iron.py`: plan by default. Execution needs **both** `--execute --allow-device-execution`, isolated inputs, one attempt and bounded timeout. They use separate private cache/home/tmp locations and retain stdout/stderr/result metadata. They are operational path guards, not an OS security sandbox. Do not run them on the current host during this investigation or while other hardware work is in progress.

Privileged configuration is documentation only; no helper silently changes kernel, firmware, system Python/XRT, groups, limits or shell startup files. No script retries installation/execution on failure. A timeout/nonzero exit is failure, with logs preserved; it is not automatically retried or converted into SKIP.

## Phase-2 validation versus unperformed integration

Offline fixtures exercise malformed model wire data, session/Run distinctions, contradictory compile-only/success logs, success with lookup diagnostics, numerical provenance/shape/NaN/tolerance checks, archive path containment, hash mismatch, receipt drift, preserved existing destinations and idempotence. These tests do not load any vendor artifact. The new C++ code is checked with `g++ -fsyntax-only` against read-only matched headers, without linking/executing.

The [phase-2 checkpoint](phase2-checkpoint.md) records exact final test commands/results and remaining limits. Linking, clean archive staging, Python imports, XRT/IRON/NPU execution and real numerical comparison are all unperformed in this phase.

## Targeted Astra follow-up

Historical versus new-acquisition manifests are explicit in [baseline policy](baseline-policy.md). `stage-cpp-sdk.py` uses `--baseline` and refuses incomplete/unreviewed inputs. [Host preflight](host-dependencies.md) rejects missing SONAMEs and out-of-candidate providers without loading code. The probe publishes a complete private result without replacement; competing publishers and symlinks cannot truncate an old result.

Added tests use mocked compiler calls and a small standalone C++ output-writer fixture without ORT/device dependencies. Only that independent fixture is linked/executed; the full probe remains syntax-only. [Astra remediation](reviews/astra-remediation.md) records updated counts and outstanding gates.
