"""Private-reference detector fixtures contain no real user locators."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('public_check', ROOT / 'scripts/check-public-tree.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class PublicTreeTests(unittest.TestCase):
    def test_private_locator_is_flagged_without_echoing_content(self):
        sample = 'https://' + 'chatgpt.com' + '/c/' + 'fixture-private-id'
        matches = check.matches('first line\n' + sample)
        self.assertEqual(matches, [{'kind': 'private_chat_locator', 'line': 2}])
        self.assertNotIn(sample, str(matches))

    def test_stable_public_evidence_ids_and_official_links_are_allowed(self):
        self.assertEqual(check.matches('HIST-C002 / REQ-001 https://github.com/microsoft/onnxruntime'), [])


if __name__ == '__main__':
    unittest.main()
