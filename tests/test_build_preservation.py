"""Build safety with tiny text fixtures and mocked compilers, no SDK execution."""
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_probe', ROOT / 'scripts/build-probe.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class BuildPreservationTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.private-evidence').mkdir(exist_ok=True, mode=0o700)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.private-evidence')
        self.root = Path(self.temp.name)
        self.sdk = self.root / '.private-work/sdk'
        self.cpp = self.sdk / 'cpp-test'
        (self.cpp / 'include').mkdir(parents=True)
        (self.cpp / 'sdk/onnxruntime/lib').mkdir(parents=True)
        (self.cpp / 'sdk/onnxruntime/lib/libonnxruntime.so').write_bytes(b'fixture library')
        (self.root / 'src').mkdir()
        for name in ['inference-probe.cpp', 'exclusive-output.hpp']:
            (self.root / 'src' / name).write_text('fixture ' + name)
        self.headers = {}
        for name in build.HEADERS:
            p = self.cpp / 'include' / name
            p.write_text('fixture ' + name)
            self.headers[name] = build.sha(p)
        self.compiler_a, self.compiler_b = self.root / 'compiler-a', self.root / 'compiler-b'
        self.compiler_a.write_text('fake compiler A')
        self.compiler_b.write_text('fake compiler B')
        self.argv = ['--sdk-root', str(self.sdk), '--apply']

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, side_effect=None):
        def compiler(argv, **kwargs):
            self.assertEqual(argv[0], str(self.compiler_a.resolve()))
            self.assertEqual(kwargs['env'], build.TOOL_ENV)
            if argv[1:] == ['--version']:
                return subprocess.CompletedProcess(argv, 0, stdout='fake compiler A 1.0\n')
            Path(argv[argv.index('-o') + 1]).write_bytes(b'fixture executable')
            return subprocess.CompletedProcess(argv, 0)
        with mock.patch.object(build, 'ROOT', self.root), mock.patch.object(build, 'HEADERS', self.headers), \
             mock.patch.dict('os.environ', {'PATH': str(self.compiler_b.parent)}), \
             mock.patch.object(build.shutil, 'which', return_value=str(self.compiler_a)) as which, \
             mock.patch.object(build.subprocess, 'run', side_effect=side_effect or compiler) as run, \
             mock.patch('sys.stdout', new_callable=io.StringIO):
            build.main(self.argv)
            which.assert_called_once_with('g++', path=build.TOOL_ENV['PATH'])
            return run

    def test_dangling_outputs_refused_before_compiler(self):
        for name in ['inference-probe', 'probe-build.json']:
            target = self.root / ('outside-' + name)
            leaf = self.cpp / name
            leaf.symlink_to(target)
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.invoke(lambda *args, **kwargs: self.fail('compiler started for an existing symlink'))
            self.assertTrue(leaf.is_symlink())
            self.assertFalse(target.exists())
            leaf.unlink()

    def test_existing_regular_file_preserved(self):
        for name in ['inference-probe', 'probe-build.json']:
            leaf = self.cpp / name
            leaf.write_bytes(b'keep')
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.invoke(lambda *args, **kwargs: self.fail('compiler started for an unowned output'))
            self.assertEqual(leaf.read_bytes(), b'keep')
            leaf.unlink()

    def test_compiler_identity_and_idempotence(self):
        run = self.invoke()
        self.assertEqual(run.call_count, 2)
        receipt = json.loads((self.cpp / 'probe-build.json').read_text())
        self.assertEqual(receipt['compiler_version'], 'fake compiler A 1.0')
        self.assertEqual(receipt['fingerprint']['compiler_realpath'], str(self.compiler_a.resolve()))
        self.assertEqual(receipt['fingerprint']['compiler_sha256'], build.sha(self.compiler_a))
        self.assertEqual(self.invoke().call_count, 0)

    def test_second_build_is_refused_while_first_lock_held(self):
        calls = []
        def compiler(argv, **kwargs):
            calls.append(argv)
            if '--version' in argv:
                return subprocess.CompletedProcess(argv, 0, stdout='fake compiler A 1.0\n')
            with self.assertRaises(ValueError):
                build.main(self.argv)
            Path(argv[argv.index('-o') + 1]).write_bytes(b'fixture executable')
            return subprocess.CompletedProcess(argv, 0)
        self.invoke(compiler)
        self.assertEqual(len(calls), 2)
        self.assertFalse((self.cpp / '.probe-build.lock').exists())

    def test_output_race_preserves_arriving_symlink(self):
        target = self.root / 'outside-receipt'
        def compiler(argv, **kwargs):
            if '--version' in argv:
                return subprocess.CompletedProcess(argv, 0, stdout='fake compiler A\n')
            Path(argv[argv.index('-o') + 1]).write_bytes(b'fixture executable')
            (self.cpp / 'probe-build.json').symlink_to(target)
            return subprocess.CompletedProcess(argv, 0)
        with self.assertRaises(ValueError):
            self.invoke(compiler)
        self.assertFalse(target.exists())
        self.assertTrue((self.cpp / 'probe-build.json').is_symlink())
        self.assertFalse((self.cpp / 'inference-probe').exists())

    def test_output_parent_symlink_is_refused(self):
        outside = self.root / 'outside-parent'
        outside.mkdir()
        alternative = self.sdk / 'cpp-real'
        self.cpp.rename(alternative)
        self.cpp.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
