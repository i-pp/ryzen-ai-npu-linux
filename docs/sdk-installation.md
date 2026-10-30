# SDK acquisition, installer behavior and the C++ subset

The historical successful path uses SDK 1.8.0 C++ deployment libraries, not a verified SDK Python 3.12 installation. Both the original-named installer E050 and local py314 variant E051 were preserved privately and left unchanged. Their four Python substitutions are Verified; byte comparison of E050 against the large original distribution member remains pending, so “vendor-style original-named file” is more precise than an independently authenticated pristine installer.

## Installer behavior verified from local source

| Operation | Behavior and classification |
|---|---|
| Arguments | `-a yes` acknowledges linked AMD/third-party EULAs; `-p` chooses new venv; optional `-c` chooses C++ deployment destination, `-n` prompt name; `-l` is deprecated. **Required only when choosing the full vendor installer route.** |
| Existing destinations | Refuses existing venv/C++ directories and suggests deletion. **Do not follow the deletion suggestion against the preserved environments.** The installer is not idempotent. |
| Interpreter | Explicit Python 3.12 calls and equality guard. Replacing them with 3.14 is **FailedHistorical**, not an accepted Python compatibility fix. |
| Capacity checks | Warns below 8 CPUs, 36 GB RAM and 50 GB free space; warnings are not proof that lower resources work or hard resource guarantees. |
| Packages | Creates venv, pip-installs uv, installs all local wheels with prereleases and extra indices/unsafe-best-match, uninstalls overlapping ORT/OGA distributions, reinstalls ORT VitisAI and OGA, then requirements_extras. Dependency resolution/network state is not fully pinned. |
| Activation | Patches bash/csh activation, library/Python paths and SDK variables. The patch describes the vendor's 24.04/Python3.12 baseline. Avoid sourcing the preserved activation scripts during inspection. |
| Deployment | Extracts LLM and deployment archives; optionally onnxruntime C++ SDK and VOE config archive; extracts quicktest. |
| Post-checks | Inspects linux-libc-dev/zip and prints a possible `/usr/include/asm` symlink suggestion. It does not demonstrate those changes were executed or necessary here. No global symlink is created by this project. |

EULA links are recorded as provenance, not a license grant: [AMD EULA](https://account.amd.com/content/dam/account/en/licenses/download/amd-end-user-license-agreement.pdf), [SDK third-party notices](https://account.amd.com/content/dam/account/en/licenses/download/ryzen-ai-1-8-0-linux-tpn-license.pdf). A fresh operator must acquire the software and review its terms through the authorized source. No authentication, acceptance receipt, or redistribution right was inferred from local possession.

## Optimized C++ branch

**Required:** manually obtain the SDK archives and official ORT v1.27.0 headers; verify their identities before staging. The [acquisition ledger](dependencies.md) records names, sizes/hashes and outstanding provenance. Historical full archive hashes remain missing. The [baseline policy](baseline-policy.md) separates that incomplete restoration from a newly acquired, reviewed new-... candidate; a new self-hash is not historical identity evidence.

`stage-cpp-sdk.py` plans/extracts only the C++ ORT archive, exact quicktest model, SDK Peano member and matched headers into `.private-work/cpp-sdk`. It never invokes the vendor installer, pip, patchelf or a vendor binary. `--apply --acknowledge-sdk-license` is an explicit future opt-in; it reads expected hashes/member contracts from the reviewed `--baseline` manifest, records its ID/kind/byte hash, and verifies input/model/header identities and the selected Peano member, uses safe archive extraction, preserves mismatched destinations, and records a file receipt. It can be rerun idempotently when the staged content is unchanged. Missing/different inputs produce FAIL, never an automatic repair.

No SDK staging was performed in phase 2; only syntax and offline safety fixtures were tested. This C++ subset is a reconstructed route from observed dependencies, not an independently executed minimal installation. The full Python/LLM/CUDA wheel set is not an established prerequisite for the quicktest.

**Optional/Conditional:** if Python SDK APIs are actually required, provision Python 3.12 separately without replacing system Python and run the unmodified installer in a new licensed isolated destination. That branch needs its own package lock, compatibility test and numerical validation. It is not currently a reproduced procedure on Ubuntu 26.04.
