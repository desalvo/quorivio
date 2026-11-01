"""RC66: independent checked GitHub evidence, no duplicate SSO credit."""
from __future__ import annotations
import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from rc_campaign_preflight import campaign_audit

class VerifiedFederatedIdentityGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        cls.gates={g['id']:g for g in cls.matrix['gates']}
        cls.receipt=json.loads((ROOT/'docs/validation/RC_CYCLE66_GITHUB_VERIFIED_20261031.json').read_text())

    def test_two_git_workflows_same_committed_source_and_no_publish(self):
        r=self.receipt
        self.assertEqual(r['standard']['head_sha'],r['extended']['head_sha'])
        self.assertEqual(r['standard']['head_sha'],'487c960f09b3c9adb996d489f44b52d059da12b2')
        self.assertEqual((r['standard']['run'],r['extended']['run']),(41191213305,41191751069))
        self.assertEqual((r['extended']['successful_campaign_job_count'],r['extended']['mandatory_campaign_job_count']),(11,11))
        self.assertFalse(r['publish_image'])
        self.assertFalse(r['strict_rc_ready'])

    def test_scope_is_new_and_narrow(self):
        parent=self.gates['C3']; protocol=self.gates['C3-AUTO']; account=self.gates['C3-PG-IDENTITY']
        self.assertEqual((parent['weight'],parent['status']),(2,'partial'))
        self.assertEqual((protocol['weight'],protocol['status']),(2,'accepted'))
        self.assertEqual((account['weight'],account['status']),(2,'accepted'))
        self.assertEqual((account['verified_run_id'],account['verified_job_id']),(41191751069,124509777927))
        self.assertEqual(account['verified_commit_sha'],self.receipt['standard']['head_sha'])
        self.assertIn('one-shot state',account['evidence'])
        self.assertIn('account-scoped',account['scope'])
        self.assertIn('Real external Google/GitHub/Facebook',parent['remaining'])
        self.assertNotEqual(account['scope'],protocol['evidence'])

    def test_reconciled_score_is_explained_and_no_other_gate_promoted(self):
        self.assertEqual(sum(x['weight'] for x in self.matrix['gates']),100)
        expected = round(sum(g['weight'] * (1 if g['status']=='accepted' else .5 if g['status']=='partial' else 0) for g in self.matrix['gates']), 2)
        self.assertEqual((audit()['score'],preflight()['score']),(expected,expected))
        self.assertEqual((preflight()['accepted_gates'],preflight()['gate_count'],len(preflight()['unaccepted_gates'])),(sum(g['status']=='accepted' for g in self.matrix['gates']),len(self.matrix['gates']),sum(g['status']!='accepted' for g in self.matrix['gates'])))
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertEqual((self.receipt['score']['old'],self.receipt['score']['new'],self.receipt['score']['delta']),(81.75,82.75,1.0))
        self.assertEqual(len(campaign_audit()['pending']),17)
        self.assertTrue(campaign_audit()['external_signoff_required'])

    def test_evidence_driven_not_bypassed(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        for line in ('run: node tools/ci_federated_link_postgres.mjs',
                     'run: node tools/ci_federated_identity_management_pg.mjs',
                     'gitleaks/gitleaks-action@v2',
                     'rc_acceptance_suite:'):
            self.assertIn(line,workflow)
        self.assertIn('python3 tools/verify_rc_cycle65_inventory.py --historical',workflow)
        self.assertIn('python3 tools/verify_rc_cycle66_inventory.py',workflow)

if __name__=='__main__':unittest.main()
