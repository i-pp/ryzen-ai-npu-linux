"""Fixtures for evidence interpretation, not hardware or SDK compatibility tests."""
import copy
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('evidence_tools', Path(__file__).resolve().parents[1] / 'scripts/evidence_tools.py')
et = importlib.util.module_from_spec(spec)
spec.loader.exec_module(et)


def vint(n):
    data = bytearray()
    while n > 127:
        data.append((n & 127) | 128)
        n >>= 7
    data.append(n)
    return bytes(data)


def field(n, value):
    if isinstance(value, str):
        value = value.encode()
    if isinstance(value, int):
        return vint(n << 3) + vint(value)
    return vint((n << 3) | 2) + vint(len(value)) + value


def value_info(name, shape):
    dims = b''.join(field(1, field(1, d)) for d in shape)
    return field(1, name) + field(2, field(1, field(1, 1) + field(2, dims)))


class OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (Path(__file__).resolve().parents[1] / '.private-evidence').mkdir(exist_ok=True, mode=0o700)

    def test_api_pass_requires_run_and_quicktest(self):
        log = 'ONNX Runtime: 1.27.0\nVitis AI EP registration: PASS\nONNX session creation: PASS\n'
        self.assertFalse(et.inference_log(log)['api_success'])
        log += 'Inference: PASS\nQuicktest: PASS\n'
        self.assertTrue(et.inference_log(log)['api_success'])
        self.assertFalse(et.inference_log(log)['reported_npu_execution'])

    def test_registration_and_partition_do_not_prove_execution(self):
        log = 'Actually running on NPU 1\nONNX session creation: PASS\nXRT is not installed\n'
        self.assertFalse(et.inference_log(log)['api_success'])
        self.assertFalse(et.inference_log(log)['reported_npu_execution'])

    def test_success_can_contain_symbol_and_detection_diagnostics(self):
        log = ('ONNX Runtime: 1.27.0\nVitis AI EP registration: PASS\n'
               'ONNX session creation: PASS\nNo. of Operators :\nNPU 398\nVITIS_EP_CPU 2\n'
               'No. of Subgraphs :\nNPU 1\nActually running on NPU 1\n'
               'undefined symbol: profiler_start\nNo driver detection supported\n'
               'Inference: PASS\nQuicktest: PASS\n')
        result = et.inference_log(log)
        self.assertTrue(result['api_success'])
        self.assertTrue(result['reported_npu_execution'])
        self.assertEqual(result['runtime_operator_counts'], {'NPU': 398, 'VITIS_EP_CPU': 2})
        self.assertEqual(result['runtime_subgraph_counts'], {'NPU': 1})
        self.assertEqual(result['symbol_lookup_diagnostic_count'], 1)
        self.assertTrue(result['driver_detection_diagnostic'])

    def test_compile_only_mixed_with_success_is_not_pass(self):
        log = ('ONNX Runtime: 1.27.0\nVitis AI EP registration: PASS\n'
               'ONNX session creation: PASS\nInference: PASS\nQuicktest: PASS\n'
               'Skipping execution in compile-only mode\n')
        self.assertFalse(et.inference_log(log)['api_success'])

    def test_iron_diagnostics_are_preserved(self):
        r = et.iron_log('warning: DMA BD reused\nPASS!\n')
        self.assertTrue(r['pass_marker'])
        self.assertFalse(r['failure_marker'])
        self.assertEqual(r['dma_warning_lines'], 1)
        self.assertTrue(et.iron_log('PASS!\nTraceback\n')['failure_marker'])

    def test_static_onnx_io(self):
        graph = field(11, value_info('input', [1, 3, 32, 32])) + field(12, value_info('output', [1, 10]))
        graph += field(1, field(4, 'Conv'))
        model = field(1, 9) + field(7, graph) + field(8, field(2, 17))
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / '.private-evidence') as d:
            p = Path(d) / 'fixture.proto'
            p.write_bytes(model)
            r = et.inspect_onnx(p)
        self.assertEqual(r['inputs'][0]['shape'], [1, 3, 32, 32])
        self.assertEqual(r['outputs'][0]['shape'], [1, 10])
        self.assertEqual(r['outputs'][0]['element_type'], 1)
        self.assertEqual(r['top_level_node_count'], 1)

    def test_truncated_or_invalid_protobuf_fails(self):
        for bad in [b'\x00', b'\x0a\x05ab', b'\x80', b'\x0b', b'\x08' + b'\xff' * 10]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                list(et.fields(bad))

    def records(self):
        ref = {'model_sha256': 'a' * 64, 'input_sha256': 'b' * 64, 'provider': 'CPU', 'onnxruntime_version': '1.27.0',
               'outputs': [{'name': 'output', 'shape': [1, 2], 'dtype': 'float32', 'values': [0.0, 1.0]}]}
        candidate = copy.deepcopy(ref)
        candidate['provider'] = 'VitisAI'
        return ref, candidate

    def test_numeric_exact_and_tolerance(self):
        r, c = self.records()
        self.assertEqual(et.compare_outputs(r, c, 0, 0)['status'], 'PASS')
        c['outputs'][0]['values'][1] = 1.001
        self.assertEqual(et.compare_outputs(r, c, .002, 0)['status'], 'PASS')
        self.assertEqual(et.compare_outputs(r, c, 0, 0)['status'], 'FAIL')

    def test_numeric_rejects_provenance_shape_and_nonfinite(self):
        for mutate in [lambda c: c.update(model_sha256='c' * 64),
                       lambda c: c.update(input_sha256='c' * 64),
                       lambda c: c.update(provider='CPU'),
                       lambda c: c.update(onnxruntime_version='1.26.0'),
                       lambda c: c['outputs'][0].update(shape=[1, 3]),
                       lambda c: c['outputs'][0].update(dtype='float64'),
                       lambda c: c['outputs'][0].update(values=[float('nan'), 1]),
                       lambda c: c['outputs'][0].update(values=[10**1000, 1]),
                       lambda c: c.update(outputs=[None]),
                       lambda c: c.update(outputs=[])]:
            r, c = self.records()
            mutate(c)
            with self.assertRaises(ValueError):
                et.compare_outputs(r, c, 0, 0)

    def test_invalid_tolerances_fail(self):
        r, c = self.records()
        for tolerance in [-1, float('inf'), float('nan')]:
            with self.assertRaises(ValueError):
                et.compare_outputs(r, c, tolerance, 0)
        with self.assertRaises(ValueError):
            et.compare_outputs([], c, 0, 0)


if __name__ == '__main__':
    unittest.main()
