"""RC68: new evidence-bounded background ownership gate from committed green GitHub CI.

This test does not turn a fake/virtual ClamAV or private CI filesystem into
physical RWX/CSI or independent production sign-off.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from rc_campaign_preflight import campaign_audit


class PrivateBackgroundEvidenceCycle68(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((ROOT / 'docs/RC_GATE_MATRIX.json').read_text())
        cls.gates = {g['id']: g for g in cls.ledger['gates']}
        cls.receipt = json.loads((ROOT / 'docs/validation/RC_CYCLE68_GITHUB_BACKGROUNDS_VERIFIED_20261031.json').read_text())

    def test_green_committed_provenance_and_no_publication(self):
        src = self.receipt['source']
        self.assertEqual(src['commit_sha'], '487c960f09b3c9adb996d489f44b52d059da12b2')
        self.assertEqual((src['standard_run_id'], src['extended_run_id']), (41191213305, 41191751069))
        self.assertEqual(src['job_id'], 124509777927)
        self.assertEqual((src['extended_conclusion'], src['job_conclusion']), ('success', 'success'))
        self.assertEqual(src['publishing_job'], 'skipped')
        self.assertFalse(self.receipt['publish_image'])
        self.assertFalse(self.receipt['strict_rc_ready'])

    def test_genuinely_distinct_authenticated_background_scope(self):
        g = self.gates
        self.assertEqual((g['C4']['weight'], g['C4']['status']), (1, 'partial'))
        self.assertEqual((g['C4-PRIVATE-BACKGROUNDS']['weight'], g['C4-PRIVATE-BACKGROUNDS']['status']), (1, 'accepted'))
        self.assertEqual((g['C4-PROFILE']['weight'], g['C4-AV-INSTREAM']['weight']), (2, 1))
        proof = g['C4-PRIVATE-BACKGROUNDS']
        self.assertEqual((proof['verified_run_id'], proof['verified_job_id']), (41191751069, 124509777927))
        self.assertEqual(proof['verified_commit_sha'], self.receipt['source']['commit_sha'])
        for phrase in ('PostgreSQL 18', 'independently owned copy', 'revocation'):
            self.assertIn(phrase, proof['scope'])
        self.assertIn('managed ClamAV', g['C4']['remaining'])
        self.assertIn('RWX', g['C4']['remaining'])
        self.assertNotEqual(proof['scope'], g['C4-PROFILE'].get('scope', 'profile assets'))

    def test_test_script_exercises_http_permissions_not_only_unit_mocks(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text()
        script = (ROOT / 'tools/ci_background_library_postgres.py').read_text()
        self.assertIn('run: python3 tools/ci_background_library_postgres.py', workflow)
        for fragment in ('/backgrounds/{original}/use', 'expected=404',
                         '/presenters/{user["id"]}', 'borrowed["background_id"]',
                         "GET',f'/api/sessions/{shared}/backgrounds/{original}/image'"):
            self.assertIn(fragment, script)
        self.assertIn(self.receipt['automated_evidence']['log_excerpt'], self.gates['C4-PRIVATE-BACKGROUNDS']['evidence'])

    def test_score_conservation_and_limits(self):
        p = preflight()
        self.assertEqual(sum(x['weight'] for x in self.ledger['gates']), 100)
        self.assertGreaterEqual(audit()['score'], 84.25)
        self.assertEqual(audit()['score'], p['score'])
        self.assertEqual(audit()['score'], campaign_audit()['certified_score'])
        self.assertGreaterEqual(p['gate_count'], 58)
        self.assertGreaterEqual(p['accepted_gates'], 41)
        self.assertEqual(len(p['unaccepted_gates']), 17)
        self.assertFalse(p['release_candidate_ready'])
        self.assertEqual(self.receipt['accounting']['after'] - self.receipt['accounting']['before'], .5)
        self.assertEqual(self.receipt['accounting']['weight_total'], 100)
        self.assertTrue(campaign_audit()['external_signoff_required'])
        self.assertIn('C4', {g['id'] for g in p['unaccepted_gates']})
        self.assertFalse(self.ledger['rc_cycle68_verified_backgrounds_reconciliation_20261031']['publish_image'])

    def test_ci_maintains_historical_receipts_and_early_gate(self):
        w = (ROOT / '.github/workflows/ci.yml').read_text()
        self.assertIn('run: python3 -m unittest tools.tests.test_rc_cycle68_verified_private_backgrounds -q', w)
        self.assertIn('python3 tools/verify_rc_cycle67_inventory.py --historical', w)
        self.assertIn('python3 tools/verify_rc_cycle68_inventory.py', w)
        self.assertIn('gitleaks/gitleaks-action@v2', w)
        self.assertIn("inputs.publish_image == true", w)


if __name__ == '__main__':
    unittest.main()
