"""Tiny synthetic SDK fixtures check containment/idempotence, not SDK operation."""
from contextlib import ExitStack
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('stage_cpp', ROOT / 'scripts/stage-cpp-sdk.py')
cpp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cpp)


def archive(path, members):
    with tarfile.open(path, mode='w:gz') as tar:
        for name, data in members.items():
            member = tarfile.TarInfo(name)
            member.size = len(data)
            tar.addfile(member, io.BytesIO(data))


class CppStagingTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.private-evidence').mkdir(exist_ok=True, mode=0o700)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / '.private-evidence')
        self.root = Path(self.tmp.name)
        self.archives, self.headers = self.root / 'archives', self.root / 'headers'
        self.archives.mkdir(); self.headers.mkdir()
        archive(self.archives / 'onnxruntime.tar.gz', {'onnxruntime/lib/libfixture.so': b'library'})
        archive(self.archives / 'quicktest.tar.gz', {'quicktest/test_model.onnx': b'model'})
        self.wheel = self.archives / 'llvm_aie-1.8.0-py3-none-linux_x86_64.whl'
        with zipfile.ZipFile(self.wheel, mode='w') as z:
            z.writestr('lnx64.o/tools/peano/lib/libpeano-lib.so.21.0git', b'peano')
        self.header_pins = {}
        for name in cpp.HEADERS:
            (self.headers / name).write_bytes(name.encode())
            self.header_pins[name] = cpp.st.digest(self.headers / name)
        self.dest = self.root / '.private-work/cpp-sdk'
        self.baseline = self.root / 'baseline.json'
        self.baseline_data = {
            'schema_version': 1, 'baseline_id': 'new-fixture-001', 'identity_kind': 'new-acquisition',
            'review_status': 'reviewed', 'acquisition_notes': 'synthetic fixture only; not a vendor source',
            'artifacts': {
                'onnxruntime': {'filename': 'onnxruntime.tar.gz', 'sha256': cpp.st.digest(self.archives / 'onnxruntime.tar.gz'), 'source_url': 'https://example.invalid/fixture', 'payload_root': 'onnxruntime'},
                'sdk_peano': {'filename': self.wheel.name, 'sha256': cpp.st.digest(self.wheel), 'source_url': 'https://example.invalid/fixture', 'payload_member': 'lnx64.o/tools/peano/lib/libpeano-lib.so.21.0git', 'payload_size_bytes': 5},
                'quicktest': {'filename': 'quicktest.tar.gz', 'sha256': cpp.st.digest(self.archives / 'quicktest.tar.gz'), 'source_url': 'https://example.invalid/fixture', 'payload_member': 'quicktest/test_model.onnx'}},
            'headers': self.header_pins, 'model_sha256': hashlib.sha256(b'model').hexdigest()}
        self.baseline.write_text(json.dumps(self.baseline_data))

    def tearDown(self):
        self.tmp.cleanup()

    def run_stage(self, extra=None):
        argv = ['stage-cpp-sdk.py', '--archives', str(self.archives), '--headers', str(self.headers),
                '--baseline', str(self.baseline), '--destination', str(self.dest),
                '--apply', '--acknowledge-sdk-license']
        with ExitStack() as stack:
            for obj, name, value in [(cpp, 'ROOT', self.root), (cpp.st, 'BASE', self.root / '.private-work'),
                                     (cpp, 'HEADERS', self.header_pins),
                                     (cpp, 'MODEL_SHA256', hashlib.sha256(b'model').hexdigest()), (cpp, 'PEANO_SIZE', 5),
                                     (sys, 'argv', argv + (extra or []))]:
                stack.enter_context(mock.patch.object(obj, name, value))
            stack.enter_context(mock.patch('sys.stdout', new_callable=io.StringIO))
            stack.enter_context(mock.patch('sys.stderr', new_callable=io.StringIO))
            cpp.main()

    def test_idempotent_stage_and_later_build_files(self):
        self.run_stage()
        (self.dest / 'cpp-test/inference-probe').write_bytes(b'new-app')
        (self.dest / 'cpp-test/probe-build.json').write_text('{}')
        self.run_stage()
        self.assertEqual((self.dest / 'cpp-test/samples/quicktest/test_model.onnx').read_bytes(), b'model')
        self.assertTrue((self.dest / 'cpp-test/peano/libpeano-lib.so').is_symlink())
        receipt = json.loads((self.dest / 'sdk-stage-receipt.json').read_text())
        self.assertEqual(receipt['inputs']['baseline']['baseline_id'], 'new-fixture-001')
        self.assertFalse(receipt['inputs']['baseline']['historical_archive_identity_claimed'])

    def test_existing_destination_preserved(self):
        self.dest.mkdir(parents=True)
        with self.assertRaises(ValueError):
            self.run_stage()
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_changed_header_rejected(self):
        (self.headers / 'onnxruntime_c_api.h').write_bytes(b'changed')
        with self.assertRaises(SystemExit):
            self.run_stage()
        self.assertFalse(self.dest.exists())

    def test_archive_traversal_rejected(self):
        archive(self.archives / 'onnxruntime.tar.gz', {'onnxruntime/../../../escape': b'bad'})
        self.baseline_data['artifacts']['onnxruntime']['sha256'] = cpp.st.digest(self.archives / 'onnxruntime.tar.gz')
        self.baseline.write_text(json.dumps(self.baseline_data))
        with self.assertRaises((ValueError, tarfile.TarError)):
            self.run_stage()
        self.assertFalse((self.root / 'escape').exists())
        self.assertFalse(self.dest.exists())

    def test_added_runtime_library_counts_as_drift(self):
        self.run_stage()
        added = self.dest / 'cpp-test/sdk/onnxruntime/lib/extra.so'
        added.write_bytes(b'extra')
        with self.assertRaises(ValueError):
            self.run_stage()
        self.assertEqual(added.read_bytes(), b'extra')

    def test_one_byte_archive_change_is_refused_by_frozen_manifest(self):
        path = self.archives / 'onnxruntime.tar.gz'
        path.write_bytes(path.read_bytes() + b'x')
        with self.assertRaises(SystemExit):
            self.run_stage()
        self.assertFalse(self.dest.exists())

    def test_missing_historical_pins_cannot_become_a_restore(self):
        self.baseline_data.update(identity_kind='historical-restore', baseline_id='historical-fixture')
        self.baseline.write_text(json.dumps(self.baseline_data))
        with self.assertRaises(ValueError):
            self.run_stage()
        self.assertFalse(self.dest.exists())

    def test_unreviewed_new_manifest_cannot_apply(self):
        self.baseline_data['review_status'] = 'pending'
        self.baseline.write_text(json.dumps(self.baseline_data))
        with self.assertRaises(ValueError):
            self.run_stage()
        self.assertFalse(self.dest.exists())


if __name__ == '__main__':
    unittest.main()
