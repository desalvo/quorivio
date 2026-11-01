"""Independent ledger contract: no new OAuth egress hardening is credited by old CI."""
import json
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight

class FederatedAuthRC(unittest.TestCase):
 def test_only_github_verified_federated_protocol_subgate_is_accepted(self):
  doc=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  gates={g['id']:g for g in doc['gates']}
  # Historical C3-AUTO protocol evidence remains immutable. RC66 separately
  # accepted PostgreSQL account management; live external providers remain partial.
  self.assertEqual((gates['C3']['weight'],gates['C3']['status']),(2,'partial'))
  self.assertEqual((gates['C3-PG-IDENTITY']['weight'],gates['C3-PG-IDENTITY']['status']),(2,'accepted'))
  self.assertEqual((gates['C3-AUTO']['weight'],gates['C3-AUTO']['status'],gates['C3-AUTO']['verified_run_id']),(2,'accepted',40638652838))
  self.assertEqual(gates['C3-AUTO']['verified_commit_sha'],'a32ef78902a656262d346a0fa622604a4deda405')
  self.assertIn('NOT real external provider',gates['C3-AUTO']['evidence'])
  self.assertIn('Google/GitHub/Facebook',gates['C3']['remaining'])
  self.assertEqual(sum(g['weight'] for g in gates.values()),100)
 def test_rc_still_requires_external_provider_and_full_new_ci(self):
  doc=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  self.assertFalse(doc['pending_local_batch']['new_feature_promoted'])
  self.assertTrue(doc['pending_local_batch']['new_ci_required'])
  self.assertGreaterEqual(audit()['score'],68)
  p=preflight()
  self.assertGreaterEqual(p['score'],68)
  self.assertGreaterEqual(p['gate_count'],33)
  self.assertGreaterEqual(p['accepted_gates'],16)
  self.assertFalse(p['release_candidate_ready'])
 def test_no_secret_in_social_profile_url_or_followed_redirect(self):
  social=(ROOT/'apps/api/src/social-oauth.ts').read_text()
  self.assertIn("headers={...headers,authorization:`Bearer ${accessToken}`}",social)
  self.assertNotIn("u.searchParams.set('access_token'",social)
  self.assertIn("method:'POST'",social)
  self.assertIn("redirect:'error'",social)
 def test_no_redirect_on_discovery_or_oidc_token_exchange(self):
  oidc=(ROOT/'apps/api/src/oidc.ts').read_text()
  server=(ROOT/'apps/api/src/server.ts').read_text()
  self.assertIn('redirect:\'error\'',oidc)
  self.assertIn("fetch(d.token_endpoint,{method:'POST',signal:AbortSignal.timeout(8000),redirect:'error'",server)
 def test_provider_contract_tests_and_documentation_present(self):
  for file in ('apps/api/test/social-oauth.test.ts','apps/api/test/oidc.test.ts'):
   self.assertIn('redirect', (ROOT/file).read_text())
  self.assertTrue((ROOT/'docs/validation/RC_OAUTH_EGRESS_AND_C3_PROTOCOL_GATE_20261028.json').is_file())
  for path in ('docs/DEVELOPMENT_STATUS.md','docs/DEVELOPMENT_STATUS.it.md'):
   # New RC cycles prepend status; the historic 67% receipt remains intact.
   content = (ROOT/path).read_text()
   self.assertIn('0.1.0-dev', content[:160])
   self.assertIn('67', content)
if __name__=='__main__':unittest.main()
