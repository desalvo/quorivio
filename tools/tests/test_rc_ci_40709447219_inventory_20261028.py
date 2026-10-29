"""CI regression: stable RC ledger contract and non-secret SHA256 evidence encoding."""
import json
import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from verify_rc_public_stage_inventory import decode_groups,validate


class RCCi40709447219Hotfix(unittest.TestCase):
    def test_pending_batch_preserves_legacy_ci_contract(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        pending=matrix['pending_local_batch']
        self.assertIs(pending['new_feature_promoted'],False)
        self.assertIs(pending['new_ci_required'],True)
        self.assertFalse(pending['gates_promoted'])
        self.assertFalse(pending['strict_rc_ready'])
        self.assertEqual(pending['last_failed_run'],40709447219)

    def test_zero_rc_credits_without_new_green_full_ci(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        gates=matrix['gates']
        self.assertGreaterEqual(len(gates),33)
        self.assertEqual(sum(x['weight'] for x in gates),100)
        self.assertGreaterEqual(sum(g['status']=='accepted' for g in gates),16)
        self.assertEqual(sum(g['status']=='partial' for g in gates),17)
        self.assertEqual(preflight()['score'],audit()['score'])
        self.assertGreaterEqual(audit()['score'],68.0)
        self.assertFalse(preflight()['release_candidate_ready'])

    def test_inventory_keeps_every_digest_without_exposing_raw_64_hex_values(self):
        path=ROOT/'docs/validation/RC_PUBLIC_STAGE_FILE_INVENTORY_20261028.json'
        report=json.loads(path.read_text(encoding='utf-8'))
        hashes=validate(path)
        self.assertEqual(len(hashes),746)
        self.assertEqual(len(set(hashes.keys())),746)
        self.assertEqual(set(hashes.keys()),set(report['files_sha256_hex_groups']))
        self.assertNotIn('files_sha256',report)
        self.assertNotIn('source_archive_sha256',report)
        self.assertIsNone(re.search(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])',path.read_text()))
        self.assertEqual(len(decode_groups(report['source_archive_sha256_hex_groups'])),64)

    def test_check_match_uses_real_hash_of_unchanged_file(self):
        import hashlib
        actual=hashlib.sha256((ROOT/'LICENSE').read_bytes()).hexdigest()
        self.assertEqual(validate()["LICENSE"],actual)

    def test_invalid_hashes_are_rejected_fail_closed(self):
        for malformed in ([], ['12345678']*7, ['1234567Z']*8, ['012345678']*8, 'a'*64, [3]*8):
            with self.subTest(malformed=str(malformed)[:25]):
                with self.assertRaises(ValueError): decode_groups(malformed)
        report=json.loads((ROOT/'docs/validation/RC_PUBLIC_STAGE_FILE_INVENTORY_20261028.json').read_text())
        with TemporaryDirectory() as t:
            p=Path(t)/'fixture.json'
            report['files_sha256_hex_groups']['LICENSE']=['deadbeef']
            p.write_text(json.dumps(report))
            with self.assertRaises(ValueError): validate(p)

    def test_ci_runs_inventory_validation_before_gitleaks(self):
        ci=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('python3 tools/verify_rc_public_stage_inventory.py',ci)
        self.assertIn('python3 tools/verify_rc_checksum_manifest.py',ci)
        self.assertLess(ci.index('Verify grouped SHA-256 evidence inventory'),ci.index('Detect credential leaks'))
        self.assertIn('gitleaks/gitleaks-action@v2',ci)


if __name__=='__main__': unittest.main()
