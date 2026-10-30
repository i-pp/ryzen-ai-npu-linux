# Ryzen AI NPU on Ubuntu 26.04

Phase 2 technical checkpoint: historical reconstruction, static cause analysis and gated reproduction tooling. **Independent clean-install reproduction and numerical model correctness have not been established.** The original successful environments were not executed, rebuilt, reinstalled or modified. No device test or system configuration change occurred.

The observed host is a GMKtec EVO-X3 / Ryzen AI MAX+ 395, Ubuntu 26.04.1, kernel 7.0.0-42-generic. Historical C++ logs show failure with a compile-only warning and later `Inference: PASS` / `Quicktest: PASS` with local XRT 2.25.37 loaded. This evidence does not establish numerical correctness or a generally reproducible installation.

Start with [current reproducibility status](docs/reproducibility-status.md), [the gated procedure](docs/reproduction-procedure.md), [causal analysis](docs/xrt-investigation.md), [chronology](docs/chronology.md) and [completeness audit](docs/completeness-audit.md). [Evidence index](docs/evidence-index.md), [phase-1 inventory](artifacts/evidence-inventory.json), [manifest](artifacts/manifest.json) and [static analysis](artifacts/static-analysis.json) distinguish current state, historical logs and new reconstructions. The [phase-2 handoff](docs/phase2-checkpoint.md) records exact validation and unresolved gates.

Run `scripts/inspect-environment.sh` only to collect a new read-only metadata snapshot. It writes a private capture beneath `.private-evidence/`, retains individual command exit states, and does not invoke XRT/IRON/inference. Unavailable probes do not mean that the physical host is broken. It is an inspection collector, not an inference or compatibility test.

Use [verification entry points](docs/verification-design.md) for JSON PASS/FAIL/SKIP checks. All verification is offline/read-only; hardware execution is separate and requires explicit flags plus a new isolated `.private-work` tree. The new C++ output probe has syntax/fixture validation only. The scripts do not imply tested vendor compatibility.

Raw evidence and future isolated staging/builds are gitignored. No SDK binaries, environments, models or archives are distributed. `artifacts/SHA256SUMS` describes external source artifacts with path aliases, not files distributed by this checkout. Five selected current container hashes are complete; historical source/member attestation and LLVM-AIE native compatibility remain unverified. SDK Python 3.12 success is not evidenced; the historical success used C++.

The source research checkpoint had no remote or publication. This separate snapshot is prepared for private GitHub backup; see [backup scope](BACKUP.md). The separate writer has supplied a [Japanese draft](articles/ryzen-ai-max-395-ubuntu-2604-npu-ja.md), and [Astra review](docs/reviews/astra-final-review.md) has returned targeted repairs. See [repair status](docs/reviews/astra-remediation.md), [baseline policy](docs/baseline-policy.md), [host dependency preflight](docs/host-dependencies.md) and [publication gates](docs/publication-gates.md). [License selection is pending](LICENSE).

The [remaining-input clarification](docs/remaining-inputs.md) now locates the SDK archives and both IRON wheel containers. The five selected container hashes are now complete; broader hashes remain deferred. The cached LLVM-AIE filename is py3-none despite internal cp310 tags. Independent fresh native/clean-host/numeric validation remains unperformed.

This export starts a fresh history from local source snapshot `7ace2d85716a267657918b99fac28798877a0d62`. Historical Git objects and private evidence are excluded. See [BACKUP.md](BACKUP.md) for the preserved scope and remaining recovery gaps.
