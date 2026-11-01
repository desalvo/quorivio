"""RC79 regression: a cumulative ZIP must include all CI-referenced manifests."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from rc_inventory_closure import check_inventory_closure, required_inventory_files
from package_rc_cumulative import assemble_paths
from verify_rc_current_inventory import current_verifier_module

CURRENT = 'docs/validation/RC_CYCLE79_PACKAGE_INVENTORY_20261031.json'
RECOVERED = 'docs/validation/RC_CYCLE77_PACKAGE_INVENTORY_20261031.json'


class InventoryClosureRC79(unittest.TestCase):
    def test_prior_cycle_receipt_matches_original_immutable_bytes(self):
        original = ''.join(('cb25830b','971a4b40','ae68dcd2','d16f7b0d','2828d97a','582fc8bb','4f5d35e5','b0c61947'))
        self.assertEqual(hashlib.sha256((ROOT / RECOVERED).read_bytes()).hexdigest(), original)

    def test_every_workflow_reference_is_in_current_inventory(self):
        current = current_verifier_module().MANIFEST
        manifest = json.loads((ROOT / current).read_text(encoding='utf8'))
        names = set(manifest['files_sha256_hex_groups']) | {current}
        required = required_inventory_files(lambda name: (ROOT / name).read_text(encoding='utf8'))
        self.assertIn(RECOVERED, required)
        self.assertIn(RECOVERED, names)
        self.assertIn('docs/validation/RC_CYCLE78_PACKAGE_INVENTORY_20261031.json', names)
        self.assertTrue(required <= names)
        self.assertGreater(check_inventory_closure(names, lambda name: (ROOT / name).read_text(encoding='utf8')), 60)

    def test_missing_previous_manifest_is_a_fatal_package_error(self):
        current = current_verifier_module().MANIFEST
        manifest = json.loads((ROOT / current).read_text(encoding='utf8'))
        names = set(manifest['files_sha256_hex_groups']) | {current}
        names.remove(RECOVERED)
        with self.assertRaisesRegex(ValueError, 'RC_CYCLE77_PACKAGE_INVENTORY'):
            check_inventory_closure(names, lambda name: (ROOT / name).read_text(encoding='utf8'))

    def test_cumulative_builder_always_recovers_all_previous_receipts(self):
        names = assemble_paths(ROOT, 'docs/validation/RC_CYCLE78_PACKAGE_INVENTORY_20261031.json', CURRENT,
                              ['tools/tests/test_rc_cycle79_inventory_closure.py', 'tools/verify_rc_cycle79_inventory.py'])
        self.assertIn(RECOVERED, names)
        self.assertIn('docs/validation/RC_CYCLE78_PACKAGE_INVENTORY_20261031.json', names)
        self.assertIn('tools/verify_rc_cycle79_inventory.py', names)
        self.assertIn('tools/package_rc_cumulative.py', names)
        self.assertNotIn(CURRENT, names)


if __name__ == '__main__':
    unittest.main()
