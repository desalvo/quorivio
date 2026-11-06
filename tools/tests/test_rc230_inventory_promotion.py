"""RC230: active release metadata and historical receipt promotion regression."""
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

from tools.verify_rc_current_inventory import current_verifier_module
from tools.verify_rc_release_status import FILES, FLAGS, verify_headers
from tools.ci_inventory_reference_guard import COMMAND, WORKFLOW, verify_references

ROOT = Path(__file__).resolve().parents[2]
RECORDED_SHA256 = {228: ['b79a3611', '461b10bd', 'be3c7304', '2959783e', '3769b92d', 'a2fe71a1', 'becfec58', '2abc4bb5'], 229: ['d17ef06f', '7f8a47fa', '8665f48d', '85391567', '3131bd7c', 'c492571b', '6facb8d0', '7a28b006']}


class RC230InventoryPromotion(unittest.TestCase):
    def test_latest_workflow_verifier_agrees_with_four_active_headers(self):
        module = current_verifier_module()
        m = re.fullmatch(r'verify_rc_cycle(\d+)_inventory', module.__name__)
        self.assertIsNotNone(m)
        cycle = int(m.group(1))
        self.assertGreaterEqual(cycle, 230)
        self.assertEqual(verify_headers(ROOT), len(FILES))
        for file in FILES:
            current = (ROOT / 'docs' / file).read_text(encoding='utf8').split('\n---\n')[0]
            self.assertIn(f'RC{cycle}', current.splitlines()[0])
            for flag in FLAGS:
                self.assertIn(flag, current)

    def test_rc227_228_229_are_historical_and_latest_is_nonhistorical(self):
        commands = COMMAND.findall((ROOT / WORKFLOW).read_text(encoding='utf8'))
        for cycle in (227, 228, 229):
            self.assertIn((f'verify_rc_cycle{cycle}_inventory.py', '--historical'), commands)
        latest = current_verifier_module().__name__ + '.py'
        self.assertEqual(commands[-1], (latest, ''))
        self.assertEqual(verify_references(ROOT, enforce_git=False), len(commands))

    def test_unchanged_historical_228_and_229_receipts(self):
        for cycle, expected in RECORDED_SHA256.items():
            receipt = next((ROOT / 'docs/validation').glob(f'RC_CYCLE{cycle}_PACKAGE_INVENTORY_*.json'))
            self.assertEqual(hashlib.sha256(receipt.read_bytes()).hexdigest(), ''.join(expected))

    def test_rc227_header_still_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'does not identify RC227'):
            verify_headers(ROOT, 227)


if __name__ == '__main__':
    unittest.main()
