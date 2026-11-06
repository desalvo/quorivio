"""RC231: Python CI test runner must resolve sibling verifiers without PYTHONPATH."""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

from tools.verify_rc_current_inventory import current_verifier_module

ROOT = Path(__file__).resolve().parents[2]


class RC231PythonImportPaths(unittest.TestCase):
    def test_current_verifier_module_is_resolved_from_project_root(self):
        self.assertEqual(current_verifier_module().__name__, 'verify_rc_cycle231_inventory')

    def test_ci_unittest_entrypoint_runs_without_pythonpath(self):
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'tools.tests.test_rc230_inventory_promotion', '-q'],
            cwd=ROOT, env=env, text=True, capture_output=True, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Ran 4 tests', result.stderr)

    def test_direct_release_script_is_also_importable_without_pythonpath(self):
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        result = subprocess.run(
            [sys.executable, 'tools/verify_rc_release_status.py'],
            cwd=ROOT, env=env, text=True, capture_output=True, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS active release metadata: 4', result.stdout)

    def test_preflight_runs_without_pythonpath_before_npm(self):
        ci = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('RC231 Python import-path verification before npm', ci)
        self.assertIn('python3 -m unittest tools.tests.test_rc231_import_paths -q', ci)
        self.assertLess(ci.index('RC231 Python import-path verification before npm'), ci.index('Validate active RC release headers'))
        self.assertIn('python3 tools/verify_rc_cycle230_inventory.py --historical', ci)
        self.assertIn('python3 tools/verify_rc_cycle231_inventory.py', ci)


if __name__ == '__main__':
    unittest.main()
