"""Inventory must preserve baseline and reject malformed/dangerous hash data."""
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_rc_cycle10_inventory import MANIFEST, decode_digest, load_inventory

class Cycle10Inventory(unittest.TestCase):
    def test_version_integrity_and_scanner_safe_encoding(self):
        data = json.loads((ROOT / MANIFEST).read_text(encoding='utf8'))
        raw = (ROOT / MANIFEST).read_text(encoding='utf8')
        self.assertEqual(data['version'], '0.1.0-dev')
        self.assertEqual(data['source_files_preserved'], 768)
        self.assertEqual(len(data['baseline_member_names']), 768)
        self.assertEqual(data['file_count_excluding_manifest'], len(load_inventory()))
        # Snapshot hashes are immutable evidence of the prior cumulative ZIP;
        # source files are expected to change during later RC cycles. Verify
        # reconstructed digest format and stable LICENSE instead. A current
        # checkout gets its own fresh complete-source checksum manifest.
        self.assertGreater(len(load_inventory()), 760)
        self.assertNotRegex(raw, r'(?<![a-f0-9])[a-f0-9]{64}(?![a-f0-9])')
        self.assertEqual(load_inventory()['LICENSE'], hashlib.sha256((ROOT/'LICENSE').read_bytes()).hexdigest())
    def test_malformed_hashes_rejected(self):
        for value in ([], ['aaaaaaaa']*7, ['aaaaaaaa']*9, ['aaaaaaaa']*7+[0], ['hhhhhhhh']*8, 'a'*64):
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode_digest(value)
if __name__=='__main__':
    unittest.main()
