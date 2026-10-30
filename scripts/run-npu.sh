#!/usr/bin/env bash
# Equivalent environment selection for a FUTURE isolated C++ run. Plan by default.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SDK_ROOT=""; XRT_ROOT=""; APP=""; APPLY=0; ALLOW=0
while (($#)); do
  case "$1" in
    --sdk-root) SDK_ROOT="${2:?missing SDK root}"; shift 2 ;;
    --xrt-root) XRT_ROOT="${2:?missing XRT root}"; shift 2 ;;
    --app) APP="${2:?missing application}"; shift 2 ;;
    --execute) APPLY=1; shift ;;
    --allow-device-execution) ALLOW=1; shift ;;
    --) shift; break ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 1 ;;
  esac
done
[[ -n "$SDK_ROOT" && -n "$XRT_ROOT" && -n "$APP" ]] || { printf '%s\n' 'Required: --sdk-root DIR --xrt-root DIR --app FILE [--execute --allow-device-execution] [-- ARGS...]' >&2; exit 1; }
SDK_ROOT="$(realpath -e -- "$SDK_ROOT")"
XRT_ROOT="$(realpath -e -- "$XRT_ROOT")"
APP="$(realpath -e -- "$APP")"
SDK_LIB="$SDK_ROOT/cpp-test/sdk/onnxruntime/lib"
PEANO_LIB="$SDK_ROOT/cpp-test/peano"
for FILE in "$SDK_LIB/libonnxruntime.so.1" "$SDK_LIB/libonnxruntime_vitisai_ep.so" "$PEANO_LIB/libpeano-lib.so.21.0git" "$XRT_ROOT/lib/libxrt_coreutil.so.2" "$XRT_ROOT/lib/libxrt_core.so.2" "$XRT_ROOT/lib/libxrt_driver_xdna.so.2"; do
  [[ -f "$FILE" ]] || { printf 'Missing required runtime file: %s\n' "$(basename -- "$FILE")" >&2; exit 1; }
done
if (( ! APPLY )); then
  printf '%s\n' 'PLAN: cwd=<SDK>; XILINX_XRT=<local-XRT>; LD_LIBRARY_PATH=<local-XRT>/lib:<SDK>/cpp-test/sdk/onnxruntime/lib:<SDK>/cpp-test/peano; app=<selected-app>'
  printf '%s\n' 'No execution, cache creation, or environment activation occurred.'
  exit 0
fi
(( ALLOW )) || { printf '%s\n' 'Execution requires --allow-device-execution on an authorized idle test host.' >&2; exit 1; }
[[ ! -L "$ROOT/.private-work" ]] || { printf '%s\n' '.private-work must not be a symlink.' >&2; exit 1; }
for DIR in "$SDK_ROOT" "$XRT_ROOT" "$APP"; do
  [[ "$DIR" == "$ROOT/.private-work/"* ]] || { printf '%s\n' 'Execution inputs must be isolated beneath this repository/.private-work.' >&2; exit 1; }
done
for FILE in "$SDK_LIB/libonnxruntime.so.1" "$SDK_LIB/libonnxruntime_vitisai_ep.so" "$PEANO_LIB/libpeano-lib.so.21.0git" "$XRT_ROOT/lib/libxrt_coreutil.so.2" "$XRT_ROOT/lib/libxrt_core.so.2" "$XRT_ROOT/lib/libxrt_driver_xdna.so.2"; do
  [[ "$(realpath -e -- "$FILE")" == "$ROOT/.private-work/"* ]] || { printf '%s\n' 'Runtime inputs must not symlink to a preserved environment.' >&2; exit 1; }
done
if (($#)); then
  (($# == 6)) || { printf '%s\n' 'Probe arguments: MODEL INPUT OUTPUT CPU|VitisAI MODEL_SHA INPUT_SHA' >&2; exit 1; }
  for FILE in "$1" "$2" "$3"; do
    [[ "$(realpath -m -- "$FILE")" == "$ROOT/.private-work/"* ]] || { printf '%s\n' 'Probe input/output paths must remain inside .private-work.' >&2; exit 1; }
  done
  [[ "$(sha256sum -- "$1" | cut -d' ' -f1)" == "$5" && "$(sha256sum -- "$2" | cut -d' ' -f1)" == "$6" ]] || { printf '%s\n' 'Supplied probe input/model hash does not match bytes.' >&2; exit 1; }
fi
# Refuse an application copied from the preserved environment with an embedded
# original absolute RUNPATH; build the reconstruction with a relative RUNPATH.
if readelf -d "$APP" | grep -F -- "$ROOT/../ryzen-ai-1.8.0" >/dev/null || readelf -d "$APP" | grep -F -- "$(dirname -- "$ROOT")/ryzen-ai-1.8.0" >/dev/null; then
  printf '%s\n' 'Application contains a preserved-environment runtime path; rebuild only in .private-work.' >&2
  exit 1
fi
RUN="$(mktemp -d "$ROOT/.private-work/run-XXXXXX")"
chmod 700 "$RUN"
mkdir -m 700 "$RUN/home" "$RUN/tmp" "$RUN/cache"
printf '%s\n' 'EXECUTION: one attempt, 180-second timeout, private log directory beneath .private-work.'
RUN_START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cd -- "$SDK_ROOT"
set +e
env -i PATH=/usr/bin:/bin LC_ALL=C HOME="$RUN/home" TMPDIR="$RUN/tmp" XDG_CACHE_HOME="$RUN/cache" \
  XILINX_XRT="$XRT_ROOT" LD_LIBRARY_PATH="$XRT_ROOT/lib:$SDK_LIB:$PEANO_LIB" LD_DEBUG=libs \
  timeout --signal=TERM --kill-after=5s 180s "$APP" "$@" >"$RUN/stdout.log" 2>"$RUN/stderr.log"
RC=$?
set -e
python3 -I -B - "$RUN" "$RC" "$APP" "$SDK_ROOT" "$XRT_ROOT" "$RUN_START" "$@" <<'PY'
import datetime,hashlib,json,sys
from pathlib import Path
run,rc,app,sdk,xrt,started,*args=sys.argv[1:]
sdk,xrt=Path(sdk),Path(xrt)
files={'application':Path(app),'ort':sdk/'cpp-test/sdk/onnxruntime/lib/libonnxruntime.so.1',
       'ep':sdk/'cpp-test/sdk/onnxruntime/lib/libonnxruntime_vitisai_ep.so',
       **{n:xrt/'lib'/('libxrt_'+n+'.so.2') for n in ['coreutil','core','driver_xdna']}}
if args:files.update(model=Path(args[0]),input=Path(args[1]))
hashes={}
for name,path in files.items():
 with path.open('rb') as stream:hashes[name]=hashlib.file_digest(stream,'sha256').hexdigest()
result={'schema_version':1,'started_utc':started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'exit_code':int(rc),'fresh_device_execution_attempted':True,'clean_install_validated':False,
        'argv':[app,*args],'cwd':str(sdk),'runtime_root':str(xrt),'completion_sha256':hashes,
        'loader_debug':'libs','environment_policy':'env -i; XRT:SDK:Peano library order; isolated HOME/cache/tmp',
        'timeout_seconds':180,'retry_count':0}
stage_receipt=sdk/'sdk-stage-receipt.json'
if stage_receipt.is_file():
 result['recorded_input_baseline']=json.loads(stage_receipt.read_text()).get('inputs',{}).get('baseline',{'identity_kind':'unknown'})
else:
 result['recorded_input_baseline']={'identity_kind':'unknown','historical_archive_identity_claimed':False}
(Path(run)/'result.json').write_text(json.dumps(result,indent=2))
PY
printf 'Execution exit=%s; logs=%s\n' "$RC" "${RUN#"$ROOT/"}"
exit "$RC"
