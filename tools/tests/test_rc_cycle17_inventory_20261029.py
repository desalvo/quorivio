"""Cycle 17 current SHA-256 source/Git/ZIP contract without altering history."""
import hashlib
import json
import pathlib
import re
import tempfile
import unittest

from verify_rc_cycle16_inventory import load_inventory as historical_16
from verify_rc_cycle17_inventory import MANIFEST, load_inventory, verify_source, verify_zip, decode_digest

ROOT=pathlib.Path(__file__).resolve().parents[2]

class RC17Integrity(unittest.TestCase):
    def test_current_source_manifest_complete(self):
        hashes=load_inventory()
        self.assertGreater(len(hashes),805)
        self.assertGreater(len(hashes), 805)  # immutable cycle-17 snapshot; current files use cycle-18 verifier
        for important in ('tools/backup_envelope.py','tools/ci_backup_restore.py',
                          'tools/tests/test_backup_envelope.py','docs/DR_ENCRYPTED_BACKUPS.it.md',
                          'docs/DR_ENCRYPTED_BACKUPS.en.md','docs/validation/RC_CYCLE16_PACKAGE_INVENTORY_20261029.json'):
            self.assertIn(important,hashes)
        self.assertEqual(hashes['LICENSE'],hashlib.sha256((ROOT/'LICENSE').read_bytes()).hexdigest())

    def test_old_manifest_is_readable_without_becoming_current_source(self):
        old=historical_16()
        self.assertEqual(len(old),805)
        self.assertNotIn('tools/backup_envelope.py',old)
        self.assertNotIn(MANIFEST,old)

    def test_digest_format_and_corruption_protection(self):
        txt=(ROOT/MANIFEST).read_text()
        self.assertNotRegex(txt,r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')
        for value in (['abcdefgh']*7,['xyz'*3]*8,'a'*64):
            with self.assertRaises(ValueError):decode_digest(value)
        with tempfile.TemporaryDirectory() as td:
            tamper=json.loads(txt)
            tamper['files_sha256_hex_groups']['LICENSE']=['fffffff0']
            invalid=pathlib.Path(td)/'bad.json';invalid.write_text(json.dumps(tamper))
            with self.assertRaises(ValueError):load_inventory(invalid)

    def test_latest_manifest_is_mandatory_in_ci(self):
        wf=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('python3 tools/verify_rc_cycle16_inventory.py --historical',wf)
        self.assertIn('python3 tools/verify_rc_cycle17_inventory.py',wf)
        self.assertLess(wf.index('python3 tools/verify_rc_cycle17_inventory.py'),wf.index('Detect credential leaks'))
        self.assertIn('gitleaks/gitleaks-action@v2',wf)

if __name__=='__main__':unittest.main()
