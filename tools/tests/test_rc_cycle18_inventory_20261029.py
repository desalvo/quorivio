"""RC cycle18 immutable digest catalog; cycle19 now validates current sources."""
import hashlib
import json
import pathlib
import re
import tempfile
import unittest
from verify_rc_cycle17_inventory import load_inventory as historical_17
from verify_rc_cycle18_inventory import MANIFEST, decode_digest, load_inventory

ROOT = pathlib.Path(__file__).resolve().parents[2]

class RC18Inventory(unittest.TestCase):
    def test_historical_cycle18_integrity_catalog(self):
        hashes = load_inventory()
        self.assertEqual(len(hashes), 823)  # immutable historical cycle-18 snapshot
        for path in ('tools/secure_instance_backup.py','tools/tests/test_secure_instance_backup.py',
                     'tools/tests/test_rc_cycle18_secure_dr_20261029.py',
                     'tools/ci_backup_restore.py', 'docs/DR_SECURE_WORKFLOW.it.md',
                     'docs/DR_SECURE_WORKFLOW.en.md', 'docs/validation/RC_CYCLE17_PACKAGE_INVENTORY_20261029.json'):
            self.assertIn(path, hashes)
        self.assertEqual(hashes['LICENSE'], hashlib.sha256((ROOT/'LICENSE').read_bytes()).hexdigest())

    def test_old_snapshot_is_historical_and_untouched(self):
        old = historical_17()
        self.assertEqual(len(old), 814)
        self.assertNotIn(MANIFEST, old)
        self.assertNotIn('tools/secure_instance_backup.py', old)

    def test_sha256_format_and_tamper_detection(self):
        text = (ROOT / MANIFEST).read_text()
        self.assertIsNone(re.search(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])', text))
        for invalid in ([], ['aaaaaaaa']*7, 'a'*64):
            with self.assertRaises(ValueError):decode_digest(invalid)
        with tempfile.TemporaryDirectory() as td:
            d = json.loads(text)
            d['files_sha256_hex_groups']['LICENSE'] = ['ffffffff']
            p = pathlib.Path(td) / 'invalid.json';p.write_text(json.dumps(d))
            with self.assertRaises(ValueError):load_inventory(p)

    def test_ci_runs_current_and_prior_history(self):
        wf=(ROOT / '.github/workflows/ci.yml').read_text()
        self.assertIn('python3 tools/verify_rc_cycle17_inventory.py --historical', wf)
        self.assertIn('python3 tools/verify_rc_cycle18_inventory.py --historical', wf)
        self.assertIn('python3 tools/verify_rc_cycle19_inventory.py', wf)
        self.assertLess(wf.index('python3 tools/verify_rc_cycle18_inventory.py'),
                        wf.index('Detect credential leaks'))

if __name__=='__main__': unittest.main()
