"""Cycle 63: historical manifests are immutable and every referenced receipt is packaged."""
from __future__ import annotations

import hashlib
import re
from datetime import date, datetime
import tempfile
import unittest
from pathlib import Path

from ci_inventory_reference_guard import ROOT, RECOVERED_RECEIPTS, verify_references


class HistoricalInventoryRecoveryTests(unittest.TestCase):
    def test_rc59_and_rc60_are_the_exact_original_archived_receipts(self):
        for cycle in (59, 60):
            name = f'docs/validation/RC_CYCLE{cycle}_PACKAGE_INVENTORY_20261031.json'
            with self.subTest(cycle=cycle):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(),
                                 RECOVERED_RECEIPTS[name])

    def test_every_workflow_manifest_is_available_before_ci_integration(self):
        self.assertGreaterEqual(verify_references(enforce_git=False), 34)

    def test_stable_current_inventory_bridge_follows_workflow(self):
        from verify_rc_current_inventory import current_verifier_module, load_inventory
        # Resolve current receipt from CI, not the previous cycle number.
        current = current_verifier_module()
        # The 20261031 suffix belongs to historical receipts, not all future
        # current receipts. Validate a real YYYYMMDD date without rewriting
        # pinned historical artifacts or relaxing source/archive checks.
        match = re.fullmatch(
            r'docs/validation/RC_CYCLE([0-9]+)_PACKAGE_INVENTORY_(20[0-9]{6})\.json',
            current.MANIFEST,
        )
        self.assertIsNotNone(match, 'unsafe or malformed current inventory name')
        cycle = int(match.group(1))
        issued = datetime.strptime(match.group(2), '%Y%m%d').date()
        self.assertGreaterEqual(cycle, 64)
        self.assertGreaterEqual(issued, date(2026, 10, 31))
        self.assertGreater(len(load_inventory()), 1100)

    def test_missing_rc59_inventory_is_detected_early(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / 'tools').mkdir()
            (repo / 'tools/verify_rc_cycle59_inventory.py').write_text(
                "MANIFEST = 'docs/validation/RC_CYCLE59_PACKAGE_INVENTORY_20261031.json'\n",
                encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'missing inventory manifest'):
                verify_references(repo, 'python3 tools/verify_rc_cycle59_inventory.py --historical',
                                  enforce_git=False)

    def test_guard_precedes_npm_and_expensive_integration(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertLess(workflow.index('Validate historical RC inventory references early'),
                        workflow.index('Install reproducibly'))
        self.assertLess(workflow.index('Validate historical RC inventory references early'),
                        workflow.index('Kubernetes wizard and worker integration tests'))

    def test_guard_requires_historical_verifiers_in_ci(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        for cycle in (59, 60, 61, 62):
            self.assertIn(f'python3 tools/verify_rc_cycle{cycle}_inventory.py --historical', workflow)


if __name__ == '__main__':
    unittest.main()
