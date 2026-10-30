# Current collected input identity — 2026-10-30

**Full SHA-256 is complete for exactly five retained local containers.** This fixes the bytes for a new collected-input baseline. It does not prove that these were the bytes used by the historical successful run, authenticate the vendor, or establish independent reproduction.

The estimate/configuration was recorded at **15:30:13.533 UTC**. Reading began **15:31:44.393 UTC** and ended **15:37:20.204 UTC**: **335.811 seconds** for **10,624,201,096 bytes**. The size/rate estimate before execution was 316.626 seconds at the maximum rate; actual average was 30.172 MiB/s.

One worker read the files sequentially with a **32 MiB/s application cap and 1 MiB buffer**, pacing each read without catch-up bursts. Launch requested `nice -n 19` and idle I/O scheduling; separate process queries did not independently observe the worker's effective scheduling. Source files were opened read-only with no-follow/no-atime flags. Device/inode/size/mtime/ctime and atime matched before/after each file. No file extraction, download, vendor import, install, build, NPU/GPU test or source-file modification occurred.

The worker checked named test-process indicators visible in its `/proc` at start/end, file boundaries and about every 30 seconds (16 observations, no matches), and checked an operator pause marker every second. This is bounded coordination evidence, not a whole-host GPU inactivity measurement. No hardware query was used.

| Container name | Bytes read | Locally computed SHA-256 |
|---|---:|---|
| `llvm_aie-22.0.0.2026102001+4f5df13d-py3-none-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl` | 149,617,848 | `63c988f06bd7359737f881443b5166ade847efd1e5d27d57d8481ee406e62d41` |
| `mlir_aie-1.4.5.dev113+ge28f6dc-cp314-cp314-manylinux_2_35_x86_64.whl` | 265,463,510 | `7af231daa7b0f6be17c570674f8f038f8a868a99ae4356cb2692982ee282bb0a` |
| `onnxruntime.tar.gz` | 914,703,902 | `51a091ce47b87a1a5a0c7df9df5ad30fc05a9797758fdda7703f891d9ce8199f` |
| `llvm_aie-1.8.0-py3-none-linux_x86_64.whl` | 1,474,908,981 | `35700efe0706324959f7b6f159250094d20157baed14345fb8d5bb2be0475308` |
| `ryzen_ai-1.8.0.tgz` | 7,819,506,855 | `7532d511532dd8842995bc8dc2edd8a45fbf261312ea9abe8dd01b4d502ac98d` |

The two wheel names come from the already-retained HTTP cache metadata; their actual `.body` aliases are in the [full record](../artifacts/collected-input-hashes.json). Those five inputs had no previously recovered whole-file digest. Every vendor-published digest/signature field remains null/false. The [SHA256SUMS](../artifacts/collected-input-SHA256SUMS) describes external aliased files, not binaries distributed by this repository. Full absolute source paths, expected inode metadata, worker/config and events remain in ignored private evidence.

## Frozen baseline and verification boundary

- [Current C++ baseline](../artifacts/baselines/new-collected-cpp-sdk-1.8.0-20261030.json): ORT and SDK Peano now pinned; earlier quicktest/header/model pins reused without rereading them. The existing helper's `new-acquisition` branch is used to distinguish this newly frozen retained-input baseline from historical restoration. No fresh download occurred. The review marker records operator review of current hashes/contracts, not independent/native acceptance.
- [Current IRON inputs](../artifacts/baselines/new-collected-iron-wheels-20261030.json): both full container hashes and previous selected WHEEL/METADATA matches. Full installed-payload equality is untested. LLVM-AIE's py3-none filename/internal cp310 metadata discrepancy and fresh native compatibility remain unresolved.
- [Historical manifest](../artifacts/baselines/historical-cpp-sdk-1.8.0.json): historical identity fields remain incomplete; separate `current_collected_sha256` references prevent substituting a current self-hash for historical evidence. Exact outer distribution member relationships/source acquisition receipt remain unverified. No streaming member comparison was added to this hash-only task.

The current C++ baseline supports a **plan-only** check with the existing helper:

```sh
python3 -I -B scripts/stage-cpp-sdk.py \
  --baseline artifacts/baselines/new-collected-cpp-sdk-1.8.0-20261030.json \
  --archives "$NPU_ARCHIVES" --headers "$NPU_HEADERS"
```

A plan without input-identity blockers is not a staged installation or successful native run. Applying still requires the existing explicit local-use/license acknowledgement and a separate isolated working tree. The [independent host acceptance scope](remaining-inputs.md) remains unchanged. Broader SDK/runtime inputs outside these five remain deferred; the original memcpy attachment remains unrecovered.
