"""Contract checks for the real PostgreSQL Chromium participant opt-in."""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parents[2]

class ParticipantBrowserAcceptance(unittest.TestCase):
 def setUp(self):
  self.script=(ROOT/'tools/ci_browser_participant.py').read_text()
  self.workflow=(ROOT/'.github/workflows/ci.yml').read_text()
  self.live=(ROOT/'tools/ci_live_http.py').read_text()
  self.api=(ROOT/'apps/api/src/server.ts').read_text()

 def test_real_browser_fixture_compiles_and_requires_loopback(self):
  ast.parse(self.script)
  self.assertIn("assert BASE.startswith('http://127.0.0.1:')",self.script)
  self.assertIn("WEB=os.environ.get('QUORIVIO_WEB_URL',BASE)",self.script)
  self.assertIn("browser.new_context",self.script)

 def test_browser_is_postgresql_backed_and_uses_production_frontend(self):
  self.assertIn('Chromium participant UI and PostgreSQL lifecycle (opt-in)',self.workflow)
  self.assertIn("python3 tools/ci_browser_participant.py",self.workflow)
  self.assertIn("curl --fail --silent http://127.0.0.1:8080/",self.workflow)
  self.assertIn('if: github.event_name == \'workflow_dispatch\' && inputs.browser_test',self.workflow)
  self.assertIn('same-origin CSRF/WebSocket policy',self.workflow)

 def test_isolated_participants_privacy_idempotency_and_mobile(self):
  for token in ['browser.new_context(viewport={\'width\':390','two isolated','await vote(p1,\'Yes\')',"await vote(p2,'No')",'await p1.reload','row[\'valid\']==2',"/report.json')).status==401",'/participation']:
   self.assertIn(token,self.script)

 def test_real_http_smoke_recovers_cookie_without_pii(self):
  self.assertIn("f'/api/join/{code}/participation'",self.live)
  self.assertIn("'joined': True",self.live)
  self.assertIn("'joined': False",self.live)
  self.assertIn("Cache-Control','no-store, private'",self.api)
  self.assertIn("res.json({joined:(found.rowCount??0)>0})",self.api)

 def test_browser_failure_artifacts_are_opt_in_and_short_lived(self):
  self.assertIn('chromium-participant-failure',self.workflow)
  self.assertIn('retention-days: 3',self.workflow)
  self.assertIn('await capture(p1',self.script)
  self.assertIn('await capture(p2',self.script)

if __name__=='__main__':unittest.main()
