"""RC157: release status imports must work under both CI invocation styles."""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/ci.yml'


class ReleaseImportPaths(unittest.TestCase):
    def run_clean(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env.pop('PYTHONPATH', None)
        return subprocess.run(
            [sys.executable, *args], cwd=ROOT, env=env,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30, check=False,
        )

    def test_historical_rc146_as_package_without_pythonpath(self):
        # Exact invocation previously failed only in the late evidence step.
        out = self.run_clean('-m', 'unittest', 'tools.tests.test_rc146_release_header_fix', '-q')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn('Ran 3 tests', out.stderr)

    def test_current_release_guard_runs_as_script_without_pythonpath(self):
        out = self.run_clean('tools/verify_rc_release_status.py')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn('4 files match the current inventory', out.stdout)

    def test_ci_sets_grouped_import_path_and_has_early_clean_preflight(self):
        workflow = WORKFLOW.read_text(encoding='utf8')
        self.assertRegex(workflow, r'(?s)- name: Verify grouped SHA-256 evidence inventory\n\s+env:\n\s+PYTHONPATH: tools\n\s+run:')
        self.assertIn('env -u PYTHONPATH python3 -m unittest tools.tests.test_rc146_release_header_fix tools.tests.test_rc157_release_import_paths -q',workflow)
        self.assertLess(workflow.index('RC157 isolated release imports'),workflow.index('name: Kubernetes wizard and worker integration tests'))

    def test_historical_receipt_not_replaced(self):
        workflow = WORKFLOW.read_text(encoding='utf8')
        self.assertIn('python3 tools/verify_rc_cycle156_inventory.py --historical', workflow)
        self.assertIn('python3 tools/verify_rc_cycle157_inventory.py',workflow)
        self.assertTrue((ROOT/'docs/validation/RC_CYCLE156_PACKAGE_INVENTORY_20261103.json').is_file())


if __name__ == '__main__':
    unittest.main()
