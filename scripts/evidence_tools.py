"""Offline evidence readers. No SDK imports, dynamic loading, or device access."""
import collections
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def command(argv, timeout=25):
    """Use only with selected metadata tools; never execute a vendor library."""
    r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                       env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
                            'GIT_OPTIONAL_LOCKS': '0'})
    if r.returncode:
        raise ValueError(f'{Path(argv[0]).name} failed, exit={r.returncode}')
    return r.stdout


def elf(path):
    text = command(['readelf', '--wide', '-d', str(path)])
    result = {'needed': [], 'rpath': [], 'runpath': [], 'soname': []}
    for kind, value in re.findall(r'\((NEEDED|RPATH|RUNPATH|SONAME)\).*?\[(.*?)\]', text):
        result[kind.lower()].append(value)
    return result


def xrt_imports(path):
    # Restrict to the xrt / xrt_core namespaces and XRT C API. A vendor function
    # whose argument happens to contain xrt::bo is not an XRT-provided symbol.
    text = command(['nm', '-D', '--undefined-only', '--format=posix', str(path)])
    return sorted({line.split()[0].split('@')[0] for line in text.splitlines()
                   if re.match(r'^(?:_ZNK?(?:3xrt|8xrt_core)|xrt[A-Z])', line)})


def defined_symbols(path):
    text = command(['nm', '-D', '--defined-only', '--format=posix', str(path)])
    return {line.split()[0].split('@')[0] for line in text.splitlines()}


def varint(data, offset):
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(data):
            raise ValueError('truncated protobuf varint')
        byte = data[offset]
        offset += 1
        if shift == 63 and byte > 1:
            raise ValueError('protobuf varint overflow')
        value |= (byte & 127) << shift
        if not byte & 128:
            return value, offset
    raise ValueError('protobuf varint overflow')


def fields(data):
    """Bounded protobuf wire inspection; this is not ONNX model validation."""
    data = memoryview(data)
    offset = 0
    while offset < len(data):
        tag, offset = varint(data, offset)
        field, wire = tag >> 3, tag & 7
        if field == 0:
            raise ValueError('invalid protobuf field zero')
        if wire == 0:
            value, offset = varint(data, offset)
        else:
            if wire == 2:
                length, offset = varint(data, offset)
            elif wire in (1, 5):
                length = 8 if wire == 1 else 4
            else:
                raise ValueError('unsupported protobuf wire type')
            end = offset + length
            if end > len(data):
                raise ValueError('truncated protobuf field')
            value, offset = data[offset:end], end
        yield field, wire, value


def first(data, number, default=None):
    return next((value for n, _, value in fields(data) if n == number), default)


def utf8(data):
    return bytes(data).decode('utf-8') if data is not None else ''


def value_info(data):
    name = utf8(first(data, 1))
    tp = first(data, 2)
    tensor = first(tp, 1) if tp is not None else None
    if tensor is None:
        return {'name': name, 'kind': 'non-tensor-or-unknown'}
    shape = first(tensor, 2)
    dims = None
    if shape is not None:
        dims = []
        for n, _, dim in fields(shape):
            if n == 1:
                value = first(dim, 1)
                dims.append(value if value is not None else utf8(first(dim, 2)) or None)
    return {'name': name, 'element_type': first(tensor, 1), 'shape': dims}


def inspect_onnx(path):
    p = Path(path)
    if p.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('model exceeds 64 MiB static inspection limit')
    data = p.read_bytes()
    graph = first(data, 7)
    if graph is None:
        raise ValueError('ModelProto has no graph')
    inputs, outputs, ops = [], [], collections.Counter()
    initializers = external_initializers = 0
    for n, _, value in fields(graph):
        if n == 1:
            ops[utf8(first(value, 7)) + '::' + utf8(first(value, 4))] += 1
        elif n in (11, 12):
            (inputs if n == 11 else outputs).append(value_info(value))
        elif n == 5:
            initializers += 1
            external_initializers += int(first(value, 14, 0) == 1)
    return {'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data),
            'ir_version': first(data, 1), 'producer': utf8(first(data, 2)),
            'opsets': [{'domain': utf8(first(v, 1)), 'version': first(v, 2)}
                       for n, _, v in fields(data) if n == 8],
            'inputs': inputs, 'outputs': outputs,
            'top_level_node_count': sum(ops.values()),
            'operators': dict(sorted(ops.items())), 'initializers': initializers,
            'external_initializers': external_initializers,
            'scope': 'top-level wire metadata only; no schema/shape/weight validation or execution'}


def clean_log(text):
    return re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text)


def inference_log(text):
    text = clean_log(text)
    stages = {name: bool(re.search(pattern, text, re.M)) for name, pattern in {
        'ort_initialized': r'ONNX Runtime:\s*1\.27\.0\b',
        'ep_registered': r'Vitis AI EP registration: PASS',
        'session_created': r'ONNX session creation: PASS',
        'inference_completed': r'^Inference: PASS\s*$',
        'quicktest_completed': r'^Quicktest: PASS\s*$',
    }.items()}
    actual = [int(n) for n in re.findall(r'Actually running on NPU\s+(\d+)', text)]
    counts = {'operators': {}, 'subgraphs': {}}
    section = None
    for line in text.splitlines():
        if 'No. of Operators' in line:
            section = 'operators'
        elif 'No. of Subgraphs' in line:
            section = 'subgraphs'
        elif section is not None:
            match = re.search(r'(?:\]\s*|^\s*)(NPU|VITIS_EP_CPU)\s+(\d+)\s*$', line)
            if match:
                counts[section][match[1]] = int(match[2])
    loaded = {}
    for name in ['coreutil', 'core', 'driver_xdna']:
        loaded[name] = bool(re.search(
            r'calling init:\s*[^\n]*xrt-2\.25\.37/opt/xilinx/xrt/lib/libxrt_'
            + name + r'\.so\.2', text))
    compile_only = bool(re.search(r'XRT is not installed|Skipping execution in compile-only mode', text))
    return {'stages': stages, 'reported_npu_subgraphs': actual,
            'runtime_operator_counts': counts['operators'], 'runtime_subgraph_counts': counts['subgraphs'],
            'historical_local_xrt_initialized': loaded, 'compile_only': compile_only,
            'symbol_lookup_diagnostic_count': len(re.findall(r'undefined symbol:', text)),
            'driver_detection_diagnostic': 'No driver detection supported' in text,
            'api_success': all(stages.values()) and not compile_only,
            'reported_npu_execution': bool(actual) and all(n > 0 for n in actual) and
                                      stages['inference_completed'] and not compile_only,
            'numeric_validation': 'SKIP: historical quicktest does not compare values',
            'scope': 'saved log content; process exit code and a fresh run are not established'}


def iron_log(text):
    text = clean_log(text)
    return {'pass_marker': bool(re.search(r'\bPASS!', text)),
            'failure_marker': bool(re.search(r'\bFAIL(?:ED)?\b|Traceback|Unsupported device', text)),
            'dma_warning_lines': sum('warning' in l.lower() and
                                     bool(re.search(r'DMA|BD|descriptor', l, re.I))
                                     for l in text.splitlines()),
            'scope': 'saved log content only; inputs, exit status and repeated-run safety require separate evidence'}


def compare_outputs(reference, candidate, atol, rtol):
    if not isinstance(reference, dict) or not isinstance(candidate, dict):
        raise ValueError('output records must be JSON objects')
    if not all(math.isfinite(t) and t >= 0 for t in [atol, rtol]):
        raise ValueError('tolerances must be finite and nonnegative')
    if reference.get('provider') != 'CPU' or candidate.get('provider') != 'VitisAI':
        raise ValueError('CPU reference and VitisAI candidate records required')
    if reference.get('onnxruntime_version') != '1.27.0' or candidate.get('onnxruntime_version') != '1.27.0':
        raise ValueError('recorded ONNX Runtime 1.27.0 required')
    for key in ['model_sha256', 'input_sha256']:
        if not re.fullmatch(r'[0-9a-f]{64}', str(reference.get(key, ''))):
            raise ValueError(f'missing reference {key}')
        if candidate.get(key) != reference[key]:
            raise ValueError(f'{key} differs')
    expected, actual = reference.get('outputs'), candidate.get('outputs')
    if not isinstance(expected, list) or not expected or not isinstance(actual, list) or len(expected) != len(actual):
        raise ValueError('nonempty matching output lists required')
    worst = 0.0
    compared = 0
    mismatches = 0
    names = set()
    for a, b in zip(expected, actual):
        if not isinstance(a, dict) or not isinstance(b, dict):
            raise ValueError('each output must be a JSON object')
        for key in ['name', 'shape', 'dtype']:
            if a.get(key) != b.get(key):
                raise ValueError(f'output {key} differs')
        if not isinstance(a.get('name'), str) or a['name'] in names:
            raise ValueError('unique output names required')
        names.add(a['name'])
        shape = a.get('shape')
        if not isinstance(shape, list) or not all(type(n) is int and n > 0 for n in shape):
            raise ValueError('positive integer output dimensions required')
        if a.get('dtype') != 'float32':
            raise ValueError('only float32 output comparison is implemented')
        count = math.prod(shape)
        av, bv = a.get('values'), b.get('values')
        if not isinstance(av, list) or not isinstance(bv, list) or len(av) != count or len(bv) != count:
            raise ValueError('output element count differs from shape')
        for x, y in zip(av, bv):
            try:
                finite = math.isfinite(x) and math.isfinite(y)
            except (TypeError, OverflowError):
                finite = False
            if type(x) not in (int, float) or type(y) not in (int, float) or not finite:
                raise ValueError('non-finite or nonnumeric output')
            error = abs(y - x)
            worst = max(worst, error)
            mismatches += int(error > atol + rtol * abs(x))
            compared += 1
    return {'status': 'PASS' if not mismatches else 'FAIL', 'elements': compared,
            'mismatches': mismatches, 'max_absolute_error': worst,
            'atol': atol, 'rtol': rtol,
            'scope': 'provided arrays only; validate their run provenance separately'}
