"""RC67: bounded existing-green GitHub browser evidence; no RC strict/publishing."""
from __future__ import annotations
import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from rc_campaign_preflight import campaign_audit

class VerifiedBrowserRehearsalGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  cls.b={x['id']:x for x in cls.matrix['gates']}
  cls.receipt=json.loads((ROOT/'docs/validation/RC_CYCLE67_GITHUB_BROWSER_VERIFIED_20261031.json').read_text())
 def test_source_is_both_green_committed_runs_no_publication(self):
  r=self.receipt
  self.assertEqual(r['source']['commit_sha'],'487c960f09b3c9adb996d489f44b52d059da12b2')
  self.assertEqual((r['source']['standard_run_id'],r['source']['extended_run_id']),(41191213305,41191751069))
  self.assertEqual((r['source']['automatic_rc_successful_jobs'],r['source']['automatic_rc_required_jobs']),(11,11))
  self.assertEqual(r['source']['publishing_job'],'skipped')
  self.assertFalse(r['strict_rc_ready']);self.assertFalse(r['publish_image'])
 def test_offline_client_is_separate_from_postgres_and_modal_focus(self):
  g=self.b
  self.assertEqual((g['B2']['weight'],g['B2']['status']),(2,'partial'))
  self.assertEqual((g['B2-DB']['weight'],g['B2-DB']['status']),(2,'accepted'))
  self.assertEqual((g['B2-CLIENT-REHEARSAL']['weight'],g['B2-CLIENT-REHEARSAL']['status']),(2,'accepted'))
  self.assertIn('hard deadline',g['B2-CLIENT-REHEARSAL']['scope'])
  self.assertIn('one-shot reactions',g['B2-CLIENT-REHEARSAL']['evidence'])
  self.assertIn('long-lived',g['B2']['remaining'])
  self.assertEqual(g['B2-CLIENT-REHEARSAL']['verified_commit_sha'],self.receipt['source']['commit_sha'])
  self.assertNotEqual(g['B2-CLIENT-REHEARSAL']['scope'],g['B2-DB']['evidence'])
 def test_source_log_proofs_have_distinct_jobs_and_mobile_and_desktop(self):
  r=self.receipt
  self.assertEqual((r['jobs']['quality'],r['jobs']['native_firefox_webkit']),(124509777927,124511576966))
  self.assertEqual(len(r['bounded_proofs']),4)
  self.assertTrue(all(p['viewports']==[1440,390] for p in r['bounded_proofs']))
  self.assertTrue(any('disabled late submissions' in p['log_excerpt'] for p in r['bounded_proofs']))
  self.assertTrue(any('one accessible dual preview' in p['log_excerpt'] for p in r['bounded_proofs']))
  self.assertTrue(any('one-shot reactions' in p['log_excerpt'] for p in r['bounded_proofs']))
 def test_scoring_and_external_signoffs_not_faked(self):
  self.assertEqual(sum(g['weight'] for g in self.matrix['gates']),100)
  a=audit();p=preflight();c=campaign_audit()
  expected = round(sum(g['weight'] * (1 if g['status']=='accepted' else .5 if g['status']=='partial' else 0) for g in self.matrix['gates']), 2)
  self.assertEqual((a['score'],p['score'],c['certified_score']),(expected,expected,expected))
  self.assertEqual((p['gate_count'],p['accepted_gates'],len(p['unaccepted_gates'])),(len(self.matrix['gates']),sum(g['status']=='accepted' for g in self.matrix['gates']),sum(g['status']!='accepted' for g in self.matrix['gates'])))
  self.assertFalse(p['release_candidate_ready']);self.assertTrue(c['external_signoff_required'])
  self.assertEqual((self.receipt['accounting']['before'],self.receipt['accounting']['after'],self.receipt['accounting']['delta_percentage_points']),(82.75,83.75,1.0))
 def test_real_ci_contains_tests_and_security_checks(self):
  w=(ROOT/'.github/workflows/ci.yml').read_text()
  for t in ('ci_rehearsal_submission_chromium.py','ci_cross_browser_rc.py','ci_rehearsal_timer_chromium.py','gitleaks/gitleaks-action@v2','publish_image == true'):
   self.assertIn(t,w)
  self.assertIn('python3 tools/verify_rc_cycle66_inventory.py --historical',w)
  self.assertIn('python3 tools/verify_rc_cycle67_inventory.py --historical',w)
if __name__=='__main__':unittest.main()
