"""Cycle 11 historical digest snapshot, score and CI boundary contracts.

Current source integrity is verified by the latest cycle inventory; cycle-11
hashes intentionally remain immutable when future cycles edit tracked files.
"""
import json
import re
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from verify_rc_cycle11_inventory import MANIFEST, load_inventory
from rc_gate_audit import audit


class Cycle11Integrity(unittest.TestCase):
    def test_historical_source_manifest_is_complete_and_secret_scanner_safe(self):
        doc=json.loads((ROOT/MANIFEST).read_text(encoding='utf8'))
        self.assertEqual(doc['version'],'0.1.0-dev')
        self.assertEqual(doc['baseline_files_preserved'],775)
        self.assertEqual(doc['file_count_excluding_manifest'],len(load_inventory()))
        self.assertTrue(all(len(digest)==64 for digest in load_inventory().values()))
        self.assertNotRegex((ROOT/MANIFEST).read_text(encoding='utf8'),r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')

    def test_no_unverified_gates_promoted(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text(encoding='utf8'))
        self.assertEqual(audit()['score'],74.0)
        self.assertEqual(sum(g['weight'] for g in matrix['gates']),100)
        self.assertEqual(len([g for g in matrix['gates'] if g['status']=='accepted']),23)
        self.assertEqual(len([g for g in matrix['gates'] if g['status']=='partial']),17)
        self.assertFalse(matrix['pending_local_batch']['new_feature_promoted'])
        self.assertTrue(matrix['pending_local_batch']['new_ci_required'])
        self.assertFalse(matrix['pending_local_batch']['strict_rc_ready'])

    def test_protected_reset_bearer_is_not_in_get_url(self):
        api=(ROOT/'apps/api/src/password-reset.ts').read_text()
        web=(ROOT/'apps/web/src/password-recovery-url.ts').read_text()
        smtp=(ROOT/'tools/ci_password_recovery_postgres.py').read_text()
        self.assertIn('u.hash=new URLSearchParams({reset_token:token}).toString()',api)
        self.assertNotIn("u.searchParams.set('reset_token',token)",api)
        self.assertIn("url.searchParams.delete('reset_token')",web)
        self.assertIn("fragment.delete('reset_token')",web)
        self.assertIn('extract_recovery_token(content)',smtp)
        self.assertIn("not link.query",smtp)

    def test_modal_focus_is_contained_and_ci_is_wired(self):
        dialog=(ROOT/'apps/web/src/rehearsal-dialog.ts').read_text()
        ci=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn("document.addEventListener('focusin', onFocusIn, true)",dialog)
        self.assertIn("document.removeEventListener('focusin', onFocusIn, true)",dialog)
        for case in ('ci_recovery_url_chromium.py','ci_rehearsal_keyboard_chromium.py',
                     'ci_rc_rehearsal_dynamic_portals_chromium.py','verify_rc_cycle11_inventory.py'):
            self.assertIn(case,ci)


if __name__=='__main__': unittest.main()
