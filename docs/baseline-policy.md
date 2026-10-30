# Historical restoration and new acquisition

A new download's self-computed hash identifies that new input; it does not prove equality with the historical successful archive. Astra R01 remains a blocker to **historical exact restoration** until those source identities are recovered.

| Mode | Input record | Scope |
|---|---|---|
| `historical-restore` | [Historical manifest](../artifacts/baselines/historical-cpp-sdk-1.8.0.json), currently `incomplete` | Known pins and gaps only. Apply is blocked by unverified historical ORT/Peano/distribution identities, exact outer member paths and historical source review. Current hashes are recorded separately, not substituted for historical identities. |
| `new-acquisition` | A private reviewed copy of [the template](../artifacts/baselines/new-acquisition.template.json), with a unique concrete `new-...` ID | A separately identified C++ trial. Never claims historical archive identity, even if header/model pins match. Fresh link/load/cold-cache Run/numerics remain unperformed. |

`stage-cpp-sdk.py --baseline FILE` reads expected archive hashes, acquisition URLs and relative member contracts from that manifest. Individual archive-hash command-line overrides were removed. Plan output lists blockers. Apply requires a complete reviewed manifest and the existing local-use/license acknowledgement. The manifest byte hash, baseline ID and identity kind are saved in the receipt. A review marker is an operator record, not a signature or independent attestation.

For a future new acquisition, copy the template privately, choose a concrete ID, acquire authorized files, record complete hashes/acquisition notes, verify the pinned header/model/member contracts, then review and freeze the manifest before apply. A one-byte input change must fail against this frozen record; do not automatically regenerate the expected hash after a mismatch. Preserve the manifest alongside the run evidence.

SDK Peano and quicktest payload member paths are known. Exact paths inside the large outer distribution remain null in the historical manifest. A new acquisition can record its own observed outer distribution path/hash without retroactively filling historical gaps.

Both IRON wheel containers are now located and fully hashed as current inputs. LLVM-AIE has a py3-none filename and internal cp310 tags; that is consistent with normal filename selection followed by an installed-tag warning, not proof of forced installation. Historical acquisition/method and fresh native compatibility remain unverified. Recover source evidence or independently test the separately frozen IRON baseline; C++ success does not supply that acceptance. Kernel/firmware identities and new host-baseline choices are treated separately in [host dependencies](host-dependencies.md).

The [selected hash pass](collected-input-hashes.md) now freezes current SDK outer/ORT/SDK Peano and two IRON containers. The [current C++ manifest](../artifacts/baselines/new-collected-cpp-sdk-1.8.0-20261030.json) uses the existing `new-acquisition` branch with `collection_kind=retained-local-inputs`: this is a newly recorded identity, not a fresh download. It is distinct from the incomplete historical-restore manifest. Source/member review and independent native acceptance remain. Broader deferred input hashes are not evidence of file loss.
