"""Missing SONAME and candidate-boundary checks using tiny metadata fixtures."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preflight', ROOT / 'scripts/preflight-cpp.py')
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)


class PreflightTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.private-evidence').mkdir(exist_ok=True, mode=0o700)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.private-evidence')
        self.directory = Path(self.temp.name)
        self.sdk, self.system = self.directory / 'sdk', self.directory / 'system'
        self.sdk.mkdir(); self.system.mkdir()
        self.app = self.sdk / 'libroot.so'
        self.app.write_text('not an ELF; fixture reader supplies metadata')

    def tearDown(self):
        self.temp.cleanup()

    def reader(self, path):
        return {'needed': ['librequired.so.1'] if path == self.app else [],
                'rpath': [], 'runpath': [], 'soname': [path.name]}

    def test_missing_soname_is_fail(self):
        result = pf.closure([self.app], [self.sdk], [self.system], {}, self.reader)
        self.assertEqual(result['static_status'], 'FAIL')
        self.assertIn('unresolved_soname', [x['kind'] for x in result['issues']])

    def test_present_full_declared_closure_is_static_only_pass(self):
        (self.system / 'librequired.so.1').write_text('fixture')
        result = pf.closure([self.app], [self.sdk], [self.system], {}, self.reader)
        self.assertEqual(result['static_status'], 'PASS')
        self.assertEqual(len(result['objects']), 2)

    def test_link_to_preserved_outside_tree_does_not_pass(self):
        outside = self.directory / 'preserved.so'
        outside.write_text('keep')
        (self.sdk / 'librequired.so.1').symlink_to(outside)
        result = pf.closure([self.app], [self.sdk], [self.system], {}, self.reader)
        self.assertEqual(result['static_status'], 'FAIL')
        self.assertIn('dependency_escapes_candidate', [x['kind'] for x in result['issues']])
        self.assertEqual(outside.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
