"""Cumulative cycle 48 must keep the true cycle 42/43 historical receipts."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from ci_inventory_reference_guard import ROOT, RECOVERED_RECEIPTS, verify_references


class Cycle48HistoricalEvidence(unittest.TestCase):
    def test_all_declared_inventory_sources_exist(self):
        self.assertGreaterEqual(verify_references(), 34)

    def test_original_immutable_receipt_bytes_are_restored(self):
        for name, digest in RECOVERED_RECEIPTS.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_a_missing_historical_catalog_fails_before_expensive_ci_tests(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / 'tools').mkdir()
            (path / 'tools/verify_rc_cycle42_inventory.py').write_text("MANIFEST = 'docs/validation/RC_CYCLE42_PACKAGE_INVENTORY_20261030.json'\n")
            with self.assertRaisesRegex(ValueError, 'missing inventory manifest'):
                verify_references(path, 'python3 tools/verify_rc_cycle42_inventory.py --historical', enforce_git=False)

    def test_ci_runs_reference_guard_before_python_suite(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text()
        self.assertLess(workflow.index('python3 tools/ci_inventory_reference_guard.py'), workflow.index('PYTHONPATH=tools python3 -m unittest discover'))
        self.assertIn('python3 tools/verify_rc_cycle47_inventory.py --historical', workflow)
        self.assertIn('python3 tools/verify_rc_cycle48_inventory.py', workflow)
        self.assertLess(workflow.index('python3 tools/verify_rc_cycle48_inventory.py'), workflow.index('Detect credential leaks'))
        self.assertNotIn('python3 tools/verify_rc_cycle48_inventory.py --historical', workflow)

    def test_release_preflight_is_not_falsely_promoted(self):
        from rc_gate_audit import audit
        self.assertEqual(audit()['score'], 80.75)


if __name__ == '__main__':
    unittest.main()
