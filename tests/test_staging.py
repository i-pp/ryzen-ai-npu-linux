"""Archive extraction is tested with in-memory fixtures, never vendor packages."""
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

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('stage_xrt', ROOT / 'scripts/stage-xrt.py')
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)


def payload(escape=False):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w') as t:
        for name, data in [('version.json', b'{"version":"2.25.37"}'),
                           ('lib/libxrt_coreutil.so.2', b'coreutil'),
                           ('lib/libxrt_core.so.2', b'core'),
                           ('lib/libxrt_driver_xdna.so.2', b'driver')]:
            m = tarfile.TarInfo('opt/xilinx/xrt/' + name)
            m.size = len(data)
            t.addfile(m, io.BytesIO(data))
        if escape:
            m = tarfile.TarInfo('opt/xilinx/xrt/escape')
            m.type = tarfile.SYMTYPE
            m.linkname = '/tmp/outside-staged-tree'
            t.addfile(m)
    return buf.getvalue()


class FakeProcess:
    def __init__(self, data):
        self.stdout = io.BytesIO(data)
    def wait(self, timeout=None):
        return 0
    def poll(self):
        return 0


class StagingTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.private-evidence').mkdir(exist_ok=True, mode=0o700)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / '.private-evidence')
        self.root = Path(self.tmp.name)
        (self.root / 'artifacts').mkdir()
        self.packages = self.root / 'packages'
        self.packages.mkdir()
        (self.packages / 'fixture.deb').write_bytes(b'fixture')
        self.lock = {'packages': [{'name': 'fixture.deb', 'sha256': hashlib.sha256(b'fixture').hexdigest()}]}
        (self.root / 'artifacts/xrt-packages.json').write_text(json.dumps(self.lock))
        self.dest = self.root / '.private-work/xrt'
        self.argv = ['stage-xrt.py', '--packages', str(self.packages), '--destination', str(self.dest), '--apply']

    def tearDown(self):
        self.tmp.cleanup()

    def run_stage(self, data=None):
        with mock.patch.object(stage, 'ROOT', self.root), mock.patch.object(stage, 'BASE', self.root / '.private-work'), \
             mock.patch.object(sys, 'argv', self.argv), mock.patch.object(stage.subprocess, 'Popen', return_value=FakeProcess(data or payload())) as process, \
             mock.patch('sys.stdout', new_callable=io.StringIO):
            stage.main()
            return process.call_count

    def test_stages_and_second_run_does_not_extract(self):
        self.assertEqual(self.run_stage(), 1)
        self.assertEqual(self.run_stage(), 0)
        self.assertEqual((self.dest / 'opt/xilinx/xrt/lib/libxrt_core.so.2').read_bytes(), b'core')

    def test_input_hash_mismatch_refuses(self):
        (self.packages / 'fixture.deb').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.run_stage()
        self.assertFalse(self.dest.exists())

    def test_drift_does_not_overwrite(self):
        self.run_stage()
        f = self.dest / 'opt/xilinx/xrt/lib/libxrt_core.so.2'
        f.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.run_stage()
        self.assertEqual(f.read_bytes(), b'changed')

    def test_existing_unowned_directory_is_preserved(self):
        self.dest.mkdir(parents=True)
        with self.assertRaises(ValueError):
            self.run_stage()
        self.assertTrue(self.dest.is_dir())

    def test_escaping_symlink_is_rejected(self):
        with self.assertRaises((ValueError, tarfile.TarError)):
            self.run_stage(payload(escape=True))
        self.assertFalse(self.dest.exists())

    def test_destination_outside_private_work_refuses(self):
        with mock.patch.object(stage, 'BASE', self.root / '.private-work'), self.assertRaises(ValueError):
            stage.destination(self.root / 'outside')


if __name__ == '__main__':
    unittest.main()
