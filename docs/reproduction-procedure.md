# Gated clean-host reproduction procedure

**Independent clean-install reproduction has not been performed.** This is a gated reconstruction/experiment plan with incomplete historical inputs, not a completed reproducible installation. Run it on a separately authorized, idle test host. Do not execute it in the preserved SDK/MLIR trees or during the concurrent LLM work. No privileged command below was run in phase 2.

Required = necessary for the selected path. Conditional = only if inspection demonstrates need or that branch is chosen. Diagnostic = gathers evidence. Optional = extends scope. FailedHistorical = useful history to understand, not an optimized step.

| Step | Class / privilege | Procedure and success criterion |
|---|---|---|
| R01 Host prerequisites | Required + Diagnostic; inspection unprivileged, provisioning Conditional/privileged | Record clean Ubuntu 26.04 identity, hardware, PCI, compiler/binutils/Python/dpkg tools and available disk. Exact old kernel/package acquisition may require archival work; never claim it was performed. [Environment](environment.md), [host package mapping/install/preflight](host-dependencies.md). |
| R02 Driver/firmware | Required state; changes Conditional/privileged | Inspect [hardware procedure](hardware-and-driver.md); matching NPU bound to amdxdna and successful firmware boot log. No SDK DKMS overlay merely to match a guide. Reboot only when needed to load changed kernel/firmware. |
| R03 Access/memlock | Required state; changes Conditional/privileged | [Permissions procedure](memory-and-permissions.md); actual ordinary-user node access and actual process limit meet the chosen snapshot/workload. Correct PAM/system-manager contexts. New login/manager lifecycle Conditional, with actual values verified. |
| R04 System XRT | Required for independent IRON/diagnostics; package changes Conditional/privileged | Obtain Ubuntu system XRT at the recorded version where available. Snapshot packages are libxrt2/libxrt-npu2/libxrt-utils/libxrt-utils-npu/python3-xrt 1:2.21.75+dfsg-4. Record repository/version; do not silently accept another version as an exact reproduction. [Validation](xrt-validation.md) is a separate opt-in device test. |
| R05 MLIR-AIE | Required for IRON only; unprivileged fresh tree | Both original-name wheel candidates now exist in pip HTTP cache with matching installed metadata. Full current container hashes/input freezing are complete; historical provenance and fresh native acceptance remain pending; py3-none filename/internal cp310 disagreement must be recorded. No force-install requirement is proven. [Setup](mlir-aie-setup.md), [retained inputs](remaining-inputs.md). |
| R06 IRON | Conditional execution on authorized test host | [Run design](iron-execution.md); retain compile/target/artifact evidence, actual exit/data equality and warnings. Current metrics are not a new acceptance result. |
| R07 Python 3.12 | Conditional for SDK Python only | Provision separately without replacing system Python. **Unperformed** and no historical successful provisioning evidence. Not required by the independent C++ route. [Compatibility](python-compatibility.md). |
| R08 SDK artifacts | Required for C++ route; manual acquisition plus unprivileged staging | Select historical restoration or a separate new-acquisition baseline, review authorized archive identities/member paths, then use the manifest-driven helper below. **Historical full archive/source identities remain missing.** [SDK](sdk-installation.md). |
| R09 Local XRT | Required historical runtime bundle; unprivileged extraction | Stage pinned base/npu/plugin user-space payload. No system XRT replacement, firmware install or DKMS action. Known hashes and default-plan helper below. |
| R10 C++ application | Required for new numeric test; unprivileged fresh build | Build newly authored probe, matching API 27 headers and selected SDK. Historical source/binary stay unchanged. New source syntax passed, linking/running not yet tested. |
| R11 Verification | Required to claim a reproduced result; explicit execution opt-in | Inspect → compatible imports/ELF closure → compile → Run with selected libraries → numerical comparison. Retain command/exit/hash/output evidence; independent host acceptance remains pending. [Verification](verification-design.md). |

The C++ route can progress independently of the blocked IRON/Python-3.12 branches. A C++ success does not complete their acceptance gates. First choose [historical restoration versus a new acquisition](baseline-policy.md); never substitute a new download's self-hash for a missing historical identity. Follow the [host package/install/preflight procedure](host-dependencies.md) for the independently chosen host baseline.

## Artifact preparation for the C++ branch

Start in this new repository. Set task-specific variables to your **new test checkout** and manually acquired input directories. None should point to a destination in the preserved working environments.

```bash
: "${NPU_REPO:?set the new repository root}"
: "${SDK_ARCHIVES:?set the licensed SDK distribution input directory}"
: "${XRT_PACKAGES:?set the XRT DEB input directory}"
: "${NPU_BASELINE:?select the historical manifest or a private reviewed new-acquisition manifest}"
cd -- "$NPU_REPO"
NPU_HEADERS="$NPU_REPO/.private-work/headers"
NPU_CPP_ROOT="$NPU_REPO/.private-work/cpp-sdk"
NPU_XRT_ROOT="$NPU_REPO/.private-work/xrt-2.25.37/opt/xilinx/xrt"
```

Acquire the two ORT headers through the [official v1.27.0 source paths](onnxruntime-integration.md), into `NPU_HEADERS`, and verify their known SHA-256. Do not copy the current host's whole include directory. Obtain the SDK via the [official acquisition ledger](dependencies.md); a private path/filename is not a redistribution permission. The historical manifest remains incomplete and blocks apply. For a distinct new acquisition, use a private copy of the candidate template, assign a unique new-... ID, record actual acquisition/complete hashes, then review and freeze it. That branch does not establish historical archive identity. No missing historical hash was manufactured here.

Review dry plans first:

```bash
python3 -I -B scripts/stage-cpp-sdk.py --archives "$SDK_ARCHIVES" --headers "$NPU_HEADERS" \
  --baseline "$NPU_BASELINE"
python3 -I -B scripts/stage-xrt.py --packages "$XRT_PACKAGES"
```

**Conditional opt-in, unprivileged, new tree only:** add `--apply --acknowledge-sdk-license` to the first command after independently reviewing terms, and `--apply` to the second. Staging executes no vendor code. XRT helper extracts only `/opt/xilinx/xrt` user-space payload, not kernel/firmware portions of the plugin DEB; no maintainer scripts run. On interruption, input/old destination and a partial directory are preserved; inspect rather than automatically deleting/retrying.

The resulting layout is:

```text
.private-work/
  cpp-sdk/cpp-test/
    include/{onnxruntime_c_api.h,onnxruntime_ep_c_api.h}
    sdk/onnxruntime/lib/...
    peano/libpeano-lib.so.21.0git
    samples/quicktest/test_model.onnx
  xrt-2.25.37/opt/xilinx/xrt/{lib,version.json,...}
```

## New build and numerical input

Before building/linking, run the static closure gate on the staged inputs; FAIL stops this branch, while SKIP means runtime/ABI acceptance remains pending:

```bash
python3 -I -B scripts/preflight-cpp.py --sdk-root "$NPU_CPP_ROOT" --xrt-root "$NPU_XRT_ROOT"
```

The helpers plan by default. On the future isolated host, use `--apply` to build the new probe and create the input; unchanged re-runs verify their receipts/bytes, while drift stops without overwrite.

```bash
python3 -I -B scripts/build-probe.py --sdk-root "$NPU_CPP_ROOT"
python3 -I -B scripts/make-input.py --output "$NPU_REPO/.private-work/input.f32le"
```

After explicit apply, inspect all inputs without executing the SDK:

```bash
bash scripts/verify-environment.sh --sdk-root "$NPU_CPP_ROOT" --xrt-root "$NPU_XRT_ROOT"
python3 -I -B scripts/verify.py model --model "$NPU_CPP_ROOT/cpp-test/samples/quicktest/test_model.onnx"
```

A return of 2 means some checks were skipped; inspect the JSON rather than ignoring it with `|| true`. File/metadata PASS is not compatible-execution PASS.

## Future execution, one attempt per provider

Define absolute paths and compute hashes from the actual bytes on that test host:

```bash
NPU_MODEL="$NPU_CPP_ROOT/cpp-test/samples/quicktest/test_model.onnx"
NPU_INPUT="$NPU_REPO/.private-work/input.f32le"
NPU_MODEL_SHA="$(sha256sum -- "$NPU_MODEL" | cut -d' ' -f1)"
NPU_INPUT_SHA="$(sha256sum -- "$NPU_INPUT" | cut -d' ' -f1)"
```

`run-npu.sh --sdk-root "$NPU_CPP_ROOT" --xrt-root "$NPU_XRT_ROOT" --app "$NPU_CPP_ROOT/cpp-test/inference-probe"` only plans. **Conditional execution:** add both explicit flags below only when the idle test host/device run is authorized:

```bash
bash scripts/run-npu.sh --sdk-root "$NPU_CPP_ROOT" --xrt-root "$NPU_XRT_ROOT" \
  --app "$NPU_CPP_ROOT/cpp-test/inference-probe" --execute --allow-device-execution -- \
  "$NPU_MODEL" "$NPU_INPUT" "$NPU_REPO/.private-work/cpu.json" CPU "$NPU_MODEL_SHA" "$NPU_INPUT_SHA"
bash scripts/run-npu.sh --sdk-root "$NPU_CPP_ROOT" --xrt-root "$NPU_XRT_ROOT" \
  --app "$NPU_CPP_ROOT/cpp-test/inference-probe" --execute --allow-device-execution -- \
  "$NPU_MODEL" "$NPU_INPUT" "$NPU_REPO/.private-work/npu.json" VitisAI "$NPU_MODEL_SHA" "$NPU_INPUT_SHA"
```

The launcher fixes `XILINX_XRT` and local-XRT:SDK:Peano library order, isolates home/cache/tmp, captures loader debug and exit metadata, uses a 180-second timeout plus five-second grace, and never retries. The probe writes a private temporary record and publishes it with no replacement only after success. Existing outputs/symlinks and competing publication are refused; a partial temporary file is not a completed result. Cold/warm cache behavior is new evidence, not a reconstructed historical condition.

Evaluate the NPU run's stdout, stderr and result.json with `verify-inference.sh` as described in [inference verification](inference-verification.md). Then compare CPU/NPU records with explicit, predeclared model-appropriate `--atol`/`--rtol`. Both successful numeric comparison **and** NPU execution evidence are needed; either alone is insufficient. Archive the full run configuration, artifact hashes, compiler/driver/firmware versions and open warnings privately, with sanitized public excerpts if later approved.

## Procedures deliberately not replayed

**FailedHistorical:** root/unlimited as routine operation, wrong systemd path, repeated hard-limit raises, global 3.12→3.14 substitution, execstack editing as an SDK Python fix, compile-only session success as inference, and system-XRT replacement to chase a misleading message. **Optional:** full source builds, broader benchmarks, model-accuracy datasets and controlled XRT-factor experiments. Each needs separate scope and evidence; none is silently performed by this recipe.

## Current retained-input baseline

The [selected five-file hash pass](collected-input-hashes.md) has completed. For a separately identified future C++ trial, the reviewed current-input manifest is `artifacts/baselines/new-collected-cpp-sdk-1.8.0-20261030.json`. It uses the existing new-acquisition branch for retained local inputs and includes current ORT/SDK Peano hashes plus earlier quicktest/header/model pins. Its official acquisition URLs are references, not recovered receipts. No staging/apply/link/load/device execution occurred; historical-restore remains incomplete. Keep the same opt-in, local-use and isolated-worktree gates above.
