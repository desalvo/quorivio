"""RC279: OAuth cross-replica guidance is verified in actual manual sources and implementation."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EN=ROOT/'docs/manuals-src/admin-guide.en.md'
IT=ROOT/'docs/manuals-src/admin-guide.it.md'
API=ROOT/'apps/api/src/server.ts'
SQL=ROOT/'apps/api/src/schema.sql'

class OAuthManualHA(unittest.TestCase):
 def test_both_manuals_explain_single_use_across_replicas(self):
  en=EN.read_text(encoding='utf8');it=IT.read_text(encoding='utf8')
  self.assertIn('OAuth state is stored in PostgreSQL and consumed once across replicas',en)
  self.assertIn('Lo stato OAuth è conservato in PostgreSQL',it)
  for content in (en,it):
   for token in ('auth_flows','DELETE FROM auth_flows','OIDC','PostgreSQL','HTTPS'):
    with self.subTest(token=token):self.assertIn(token,content)
 def test_claim_is_supported_by_both_callback_paths(self):
  src=API.read_text(encoding='utf8')
  schema=SQL.read_text(encoding='utf8')
  self.assertIn('CREATE TABLE IF NOT EXISTS auth_flows(',schema)
  self.assertIn('state_hash text PRIMARY KEY',schema)
  self.assertIn("kind='oidc' AND expires_at>now() RETURNING",src)
  self.assertIn("kind='social' AND expires_at>now() RETURNING",src)
  self.assertIn("INSERT INTO auth_flows(state_hash,kind,provider",src)
  self.assertIn('hash(state)',src)
 def test_both_guides_warn_about_single_use_and_failover(self):
  for p in (EN,IT):
   s=p.read_text(encoding='utf8').lower()
   for term in ('callback','provider','replica','failover'):
    self.assertIn(term,s)
  self.assertNotIn('OAuth state is process-local',EN.read_text())
if __name__=='__main__':unittest.main()
