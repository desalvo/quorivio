"""RC232: real PDF/PPTX integration must run only after installing native dependencies.

This pre-npm test is dependency-free: it validates *workflow scheduling* instead
of attempting conversion on a fresh runner without Poppler or ReportLab.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / '.github/workflows/ci.yml'


class RC232ConversionCIOrder(unittest.TestCase):
    @staticmethod
    def assert_workflow_contract(workflow: str) -> None:
        # Check the actual job steps rather than documentation snippets.
        install_step = '      - name: Install Python conversion and load-test dependencies\n'
        native_step = '      - name: RC232 PDF/PPTX converter boundary after native dependencies\n'
        preflight_step = '      - name: RC229 consolidated legacy UI and converter preflight before npm\n'
        global_suite_step = '      - name: Kubernetes wizard and worker integration tests\n'
        for marker in (install_step, native_step, preflight_step, global_suite_step):
            if workflow.count(marker) != 1:
                raise AssertionError('Missing or repeated CI step: ' + marker.strip())
        preflight = workflow.index(preflight_step)
        install = workflow.index(install_step)
        native = workflow.index(native_step)
        global_suite = workflow.index(global_suite_step)
        if not preflight < install < native < global_suite:
            raise AssertionError('Native converter acceptance must follow dependency installation')
        if 'tools.tests.test_rc_conversion_30_cycle' in workflow[:install]:
            raise AssertionError('Real converter tests cannot run in the dependency-free preflight')
        install_body = workflow[install:native]
        for expected in ('poppler-utils', 'libreoffice-impress', "'reportlab>=4,<5'",
                         'command -v pdfinfo', 'command -v pdftoppm',
                         'command -v libreoffice'):
            if expected not in install_body:
                raise AssertionError('Mandatory native conversion dependency missing: ' + expected)
        native_body = workflow[native:global_suite]
        if not re.search(r'^\s+run:\s*python3 -m unittest tools\.tests\.test_rc_conversion_30_cycle -q\s*$',
                         native_body, re.M):
            raise AssertionError('Standalone real converter acceptance is no longer mandatory')
        # Preserve independent full-suite discovery; don't trade CI coverage for speed.
        if 'PYTHONPATH=tools python3 -m unittest discover -s tools/tests -v' not in workflow[global_suite:]:
            raise AssertionError('Global Python discovery must still run')

    def test_rc232_has_native_dependencies_before_real_conversion_tests(self):
        self.assert_workflow_contract(CI.read_text(encoding='utf8'))

    def test_without_poppler_install_rejected(self):
        self._mutation_rejected('poppler-utils', 'not-installed-poppler')

    def test_without_libreoffice_install_rejected(self):
        self._mutation_rejected('libreoffice-impress', 'not-installed-libreoffice')

    def test_without_reportlab_install_rejected(self):
        self._mutation_rejected("'reportlab>=4,<5'", "'reportlab-not-installed'")

    def test_moving_real_conversion_to_pre_npm_rejected(self):
        workflow = CI.read_text(encoding='utf8')
        step = '      - name: RC229 consolidated legacy UI and converter preflight before npm\n'
        broken = workflow.replace(step, step + '        run: python3 -m unittest tools.tests.test_rc_conversion_30_cycle -q\n', 1)
        with self.assertRaisesRegex(AssertionError, 'dependency-free preflight'):
            self.assert_workflow_contract(broken)

    def test_removing_mandatory_post_install_step_rejected(self):
        workflow = CI.read_text(encoding='utf8')
        broken = workflow.replace('run: python3 -m unittest tools.tests.test_rc_conversion_30_cycle -q',
                                  'run: python3 -c "print(0)"', 1)
        with self.assertRaisesRegex(AssertionError, 'no longer mandatory'):
            self.assert_workflow_contract(broken)

    def test_rc231_receipt_stays_historical_and_rc232_is_current(self):
        workflow = CI.read_text(encoding='utf8')
        self.assertIn('python3 tools/verify_rc_cycle231_inventory.py --historical', workflow)
        # RC232 remains an immutable historical receipt after future promotions.
        self.assertIn('python3 tools/verify_rc_cycle232_inventory.py --historical', workflow)
        current = re.findall(r'^\s+python3 tools/verify_rc_cycle([0-9]+)_inventory.py\s*$', workflow, re.M)
        # RC8 and RC10 retain their historic nonhistorical compatibility mode.
        self.assertEqual(sorted(int(x) for x in current if int(x) < 20), [8, 10])
        current_recent = [int(x) for x in current if int(x) >= 200]
        self.assertEqual(len(current_recent), 1, 'Exactly one modern current inventory is allowed')
        self.assertGreaterEqual(current_recent[0], 233)

    def _mutation_rejected(self, expected: str, replacement: str) -> None:
        workflow = CI.read_text(encoding='utf8')
        self.assertIn(expected, workflow)
        with self.assertRaisesRegex(AssertionError, 'dependency missing'):
            self.assert_workflow_contract(workflow.replace(expected, replacement, 1))


if __name__ == '__main__':
    unittest.main()
