"""Compile/run only the independent result writer fixture; never ORT or a device."""
from pathlib import Path
import select
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OutputWriterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++', path='/usr/bin:/bin')
        if not compiler:
            raise unittest.SkipTest('host C++ compiler not available for standalone writer fixture')
        (ROOT / '.private-evidence').mkdir(exist_ok=True, mode=0o700)
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / '.private-evidence')
        cls.directory = Path(cls.temp.name)
        cls.writer = cls.directory / 'output-writer'
        subprocess.run([str(Path(compiler).resolve()), '-std=c++17', '-Wall', '-Wextra', '-Werror',
                        '-I', str(ROOT / 'src'), str(ROOT / 'tests/fixtures/output-writer.cpp'), '-o', str(cls.writer)],
                       check=True, timeout=30, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.case = tempfile.TemporaryDirectory(dir=self.directory)
        self.dest = Path(self.case.name) / 'result.json'

    def tearDown(self):
        self.case.cleanup()

    def run_writer(self, *extra):
        return subprocess.run([str(self.writer), str(self.dest), 'new', *extra],
                              capture_output=True, text=True, timeout=5)

    def test_regular_existing_output_is_preserved(self):
        self.dest.write_text('old')
        self.assertEqual(self.run_writer().returncode, 1)
        self.assertEqual(self.dest.read_text(), 'old')

    def test_dangling_symlink_is_preserved_without_creating_target(self):
        target = self.dest.with_name('outside-missing')
        self.dest.symlink_to(target)
        self.assertEqual(self.run_writer().returncode, 1)
        self.assertTrue(self.dest.is_symlink())
        self.assertFalse(target.exists())

    def test_failed_record_is_not_visible(self):
        self.assertEqual(self.run_writer('--fail').returncode, 1)
        self.assertFalse(self.dest.exists())
        self.assertEqual(list(self.dest.parent.glob('.npu-result-*')), [])

    def test_two_prepared_writers_only_publish_one_record(self):
        processes = [subprocess.Popen([str(self.writer), str(self.dest), text, '--wait'],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for text in ['record-A', 'record-B']]
        try:
            for process in processes:
                self.assertTrue(select.select([process.stdout], [], [], 5)[0], 'writer readiness timeout')
                self.assertEqual(process.stdout.readline().strip(), 'READY')
            self.assertFalse(self.dest.exists())
            for process in processes:
                process.stdin.write('\n'); process.stdin.flush()
            for process in processes:
                process.communicate(timeout=5)
            self.assertEqual(sorted(p.returncode for p in processes), [0, 1])
            self.assertIn(self.dest.read_text(), ['record-A', 'record-B'])
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill(); process.communicate(timeout=5)


if __name__ == '__main__':
    unittest.main()
