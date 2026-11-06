"""RC209 pre-dependency regression: management from 'Apri sessione' does not open a session.

The compiled-browser + PostgreSQL integration jobs remain required for release acceptance.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
WEB=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
API=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf-8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')

class RC209OpenSessionActions(unittest.TestCase):
 def test_buttons_in_open_session_listing(self):
  fragment=WEB.split("dashboardPage==='open'&&<section",1)[1].split("dashboardPage==='new'",1)[0]
  for token in ('resetListedSession(s)','deleteListedSession(s)','canResetListedSession(', 'canDeleteListedSession(', 'Elimina sessione','Resetta a non avviata','listSessionBusy!==null'):
   self.assertIn(token,fragment)
  self.assertIn('access_role',fragment)

 def test_actions_do_not_depend_on_open_dashboard(self):
  fragment=WEB.split('async function resetListedSession(session:Session)',1)[1].split('async function duplicateSessionFrom(',1)[0]
  for token in ('session.id','window.confirm(',"'RESET_SESSION_RESULTS'", "method:'DELETE'",'await load()','listSessionBusyRef.current'):
   self.assertIn(token,fragment)
  self.assertNotIn('document.cookie',fragment)

 def test_server_explicit_owner_confirmation_and_closed_recovery(self):
  fragment=API.split("app.post('/api/sessions/:id/reset-to-ready'",1)[1].split("app.post('/api/sessions/:id/activities/:aid/close'",1)[0]
  for token in ('owner_id=$2 FOR UPDATE',"'active','paused','closed'",'RESET_SESSION_RESULTS','DELETE FROM participants', 'session_asset_file_cleanup_jobs','status=\'ready\'','GREATEST(expires_at'):
   self.assertIn(token,fragment)
  deletion=API.split("app.delete('/api/sessions/:id'",1)[1].split('// A session may be auto-purged',1)[0]
  self.assertIn('owner_id!==auth(req)',deletion)

 def test_required_early_ci_gate(self):
  self.assertIn('tools.tests.test_rc209_open_session_actions',CI)
  self.assertIn('apps/web/test/rc209-session-list-management.test.ts',CI)

if __name__=='__main__':unittest.main()
