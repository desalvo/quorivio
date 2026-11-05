"""RC202: prevent recurrence of CI #42105427044's missing Pillow/pptx preflight.

RC200 source-contract tests remain fast and dependency-free; the native
image/PPTX round-trip tests must run *after* conversion dependencies install.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/ci.yml'
TESTS = ROOT / 'tools/tests/test_rc200_editor_portability.py'


class RC202DependencyStaging(unittest.TestCase):
    def setUp(self):
        ci = WORKFLOW.read_text(encoding='utf-8')
        self.assertEqual(ci.count('- name: Install Python conversion and load-test dependencies'), 1)
        self.preflight, self.after_install = ci.split('- name: Install Python conversion and load-test dependencies', 1)

    def test_rc200_pure_contracts_remain_in_dependency_free_preflight(self):
        self.assertIn('tools.tests.test_rc200_editor_portability.RC200EditorPortability -q', self.preflight)
        self.assertIn('tools.tests.test_rc202_dependency_staging -q', self.preflight)
        self.assertNotIn('tools.tests.test_rc200_editor_portability -q', self.preflight)
        self.assertNotIn('RC200NativePowerPointPortability', self.preflight)

    def test_real_pptx_cases_are_explicit_and_after_dependencies(self):
        self.assertIn("'python-pptx>=1.0,<2'", self.after_install)
        self.assertIn("'Pillow>=11,<14'", self.after_install)
        import_check = self.after_install.index("python3 -c 'import pptx, aiohttp'")
        pillow_check = self.after_install.index("python3 -c 'import PIL'")
        native_case = self.after_install.index('tools.tests.test_rc200_editor_portability.RC200NativePowerPointPortability -v')
        full_suite = self.after_install.index('python3 -m unittest discover -s tools/tests -v')
        self.assertLess(import_check, native_case)
        self.assertLess(pillow_check, native_case)
        self.assertLess(native_case, full_suite)
        self.assertIn('def test_raster_snapshot_round_trip_to_editable_pptx(self):', TESTS.read_text(encoding='utf8'))
        self.assertIn('def test_missing_snapshot_fails_closed(self):', TESTS.read_text(encoding='utf8'))

    def test_python_unittest_loader_separates_source_and_native_cases(self):
        import tools.tests.test_rc200_editor_portability as rc200
        source = unittest.defaultTestLoader.loadTestsFromTestCase(rc200.RC200EditorPortability)
        native = unittest.defaultTestLoader.loadTestsFromTestCase(rc200.RC200NativePowerPointPortability)
        self.assertEqual(source.countTestCases(), 4)
        self.assertEqual(native.countTestCases(), 2)
        self.assertNotIn('PIL', rc200.RC200EditorPortability.__dict__)


if __name__ == '__main__':
    unittest.main()
