"""RC59 one-click non-publishing campaign and bounded identity provider transport."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_campaign_preflight import campaign_audit,OPTIONS
from rc_campaign_result_gate import evaluate_results,REQUIRED_JOBS
from rc_gate_audit import audit
from rc_release_preflight import preflight
class CampaignContracts(unittest.TestCase):
 def test_one_click_dispatch_covers_all_13_opt_in_flags(self):
  r=campaign_audit()
  self.assertEqual(len(OPTIONS),13)
  self.assertEqual(len(r['pending']),17)
  self.assertTrue(r['dispatch']['rc_acceptance_suite'])
  self.assertFalse(r['dispatch']['rc_strict'])
  self.assertFalse(r['dispatch']['publish_image'])
 def test_score_is_evidence_based_and_strict_rc_remains_blocked(self):
  self.assertEqual((audit()['score'],preflight()['score']),(audit()['score'],audit()['score']))
  self.assertFalse(preflight()['release_candidate_ready'])
 def test_independent_conclusion_fails_on_skipped_cancelled_failed_jobs(self):
  jobs={x:{'result':'success'} for x in REQUIRED_JOBS}
  self.assertTrue(evaluate_results(jobs)['ok'])
  for result in ('skipped','cancelled','failure'):
   c={**jobs,'kubernetes-https-ingress':{'result':result}}
   self.assertFalse(evaluate_results(c)['ok'])
   self.assertEqual(evaluate_results(c)['completed'],len(jobs)-1)
 def test_conclusion_fails_on_missing_extra_or_invalid_job(self):
  jobs={x:{'result':'success'} for x in REQUIRED_JOBS}
  with self.assertRaises(ValueError):evaluate_results({k:v for k,v in jobs.items() if k!='cross-browser'})
  with self.assertRaises(ValueError):evaluate_results({**jobs,'unexpected':{'result':'success'}})
  with self.assertRaises(ValueError):evaluate_results({**jobs,'cross-browser':{'result':'invalid'}})
 def test_workflow_is_explicit_and_does_not_publish(self):
  y=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn("inputs.publish_image == true && (github.ref == 'refs/heads/main'",y)
  self.assertIn('Fail closed on skipped, cancelled or failed RC campaign jobs',y)
  self.assertIn('RC_CAMPAIGN_NEEDS_JSON: ${{ toJSON(needs) }}',y)
  self.assertIn('test "$RC_CAMPAIGN_PUBLISH" = \'false\'',y)
  self.assertIn('test "$RC_CAMPAIGN_STRICT" = \'false\'',y)
 def test_17_pending_gates_have_weight_not_recredited(self):
  report=campaign_audit()
  self.assertEqual(len({g['id'] for g in report['pending']}),17)
  self.assertEqual(sum(g['weight'] for g in report['pending']), sum(g['weight'] for g in __import__('json').loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())['gates'] if g['status']!='accepted'))
  self.assertTrue(report['external_signoff_required'])
 def test_manual_generator_corrects_oauth_cross_replica_state(self):
  s=(ROOT/'tools/generate_manuals.py').read_text()
  self.assertIn('OAuth state is stored in PostgreSQL and consumed once across replicas',s)
  self.assertNotIn('OAuth state is process-local',s)
 def test_bounded_provider_json(self):
  for p in ('apps/api/src/oidc.ts','apps/api/src/social-oauth.ts','apps/api/src/server.ts'):
   self.assertIn('boundedFederatedJson',(ROOT/p).read_text())
  self.assertNotIn('await tokenReply.json()', (ROOT/'apps/api/src/server.ts').read_text())
 def test_cycle59_is_historical_and_current_is_61(self):
  y=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('python3 tools/verify_rc_cycle58_inventory.py --historical',y)
  self.assertIn('python3 tools/verify_rc_cycle59_inventory.py --historical',y)
  self.assertIn('python3 tools/verify_rc_cycle61_inventory.py',y)
  from verify_rc_current_inventory import verify_source,load_inventory
  self.assertEqual(verify_source(),len(load_inventory()))
if __name__=='__main__':unittest.main()
