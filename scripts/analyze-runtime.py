#!/usr/bin/env python3
"""Static ELF/ONNX evidence. Does not dlopen, ldd, import SDK, or execute tests."""
import argparse
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('evidence_tools', Path(__file__).with_name('evidence_tools.py'))
et = importlib.util.module_from_spec(spec)
spec.loader.exec_module(et)

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--sdk-root', type=Path, required=True)
p.add_argument('--system-xrt', type=Path, default=Path('/usr/lib/x86_64-linux-gnu/libxrt_coreutil.so.2'))
a = p.parse_args()
sdk = a.sdk_root
lib = sdk / 'cpp-test/sdk/onnxruntime/lib'
xrt = sdk / 'xrt-2.25.37/opt/xilinx/xrt'
files = {'quicktest': sdk / 'cpp-test/quicktest',
         'ort': lib / 'libonnxruntime.so.1',
         'ep': lib / 'libonnxruntime_vitisai_ep.so',
         'dispatch': lib / 'libdyn_dispatch_core.so',
         'vaiml2': lib / 'libvaiml2.so',
         'compiler': lib / 'libaiecompiler_client.so',
         'xcompiler': lib / 'libxcompiler-mlir-e2e.so',
         'peano': sdk / 'cpp-test/peano/libpeano-lib.so.21.0git',
         'system_coreutil': a.system_xrt,
         'local_coreutil': xrt / 'lib/libxrt_coreutil.so.2',
         'local_core': xrt / 'lib/libxrt_core.so.2',
         'local_driver': xrt / 'lib/libxrt_driver_xdna.so.2'}
result = {'scope': 'static inspection, no dynamic loading or execution', 'elf': {}}
for key, path in files.items():
    obj = et.elf(path)
    # Embedded absolute RPATH belongs in private evidence only. Public output
    # aliases the supplied SDK location, with no guessed host identity.
    for field in ['rpath', 'runpath']:
        obj[field] = [':'.join('<vendor-build-path>' if part.startswith('/__w/') else part
                              for part in s.replace(str(sdk.resolve()), '<SDK>').split(':'))
                      for s in obj[field]]
    obj['size_bytes'] = path.stat().st_size
    if path.stat().st_size <= 64 * 1024 * 1024:
        obj['sha256'] = et.sha256(path)
    else:
        obj['sha256_status'] = 'deferred above 64 MiB'
    result['elf'][key] = obj
system = et.defined_symbols(a.system_xrt)
local = et.defined_symbols(files['local_coreutil'])
result['xrt_namespace_imports'] = {}
for key in ['ep', 'dispatch']:
    imports = et.xrt_imports(files[key])
    result['xrt_namespace_imports'][key] = {
        'count': len(imports), 'missing_system': sorted(set(imports) - system),
        'missing_local': sorted(set(imports) - local),
        'caveat': 'unversioned name presence only; no C++ layout, semantics, dynamic lookup, plugin, or runtime compatibility proof'}
result['model'] = et.inspect_onnx(sdk / 'cpp-test/samples/quicktest/test_model.onnx')
result['headers'] = {}
for name in ['onnxruntime_c_api.h', 'onnxruntime_ep_c_api.h']:
    header = sdk / 'cpp-test/include' / name
    result['headers'][name] = {'sha256': et.sha256(header), 'size_bytes': header.stat().st_size}
print(json.dumps(result, indent=2))
