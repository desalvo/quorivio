"""Admin directory saves nickname, role and approval in one transaction."""
import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
WEB=(ROOT/'apps/web/src/main.tsx').read_text()
HTTP=(ROOT/'tools/ci_portable_http.py').read_text()
ROUTE=API.split("app.patch('/api/admin/users/:id',",1)[1].split("app.delete('/api/admin/users/:id'",1)[0]
PAGE=WEB.split("dashboardPage==='users'&&<section",1)[1].split("dashboardPage==='settings'&&<section",1)[0]
class AdminAtomicSaveTests(unittest.TestCase):
 def test_admin_required(self):self.assertIn('requireAuth,requireAdmin',ROUTE)
 def test_one_transaction(self):
  for marker in ("await cx.query('BEGIN')","await cx.query('COMMIT')","await cx.query('ROLLBACK')","finally{cx.release()}"):self.assertIn(marker,ROUTE)
 def test_row_lock(self):self.assertIn('FOR UPDATE',ROUTE)
 def test_single_update_all_fields(self):
  self.assertIn('SET role=$2,approved=$3',ROUTE)
  self.assertIn('nickname=CASE WHEN $4::boolean THEN $5::text ELSE nickname END',ROUTE)
 def test_legacy_omitted_nickname_preserved(self):self.assertIn('hasNickname',ROUTE)
 def test_primary_admin_immutable(self):self.assertIn('primary_admin_immutable',ROUTE)
 def test_self_demote_prohibited(self):self.assertIn('cannot_demote_self',ROUTE)
 def test_nickname_collision_is_conflict(self):self.assertIn("(e as any)?.code==='23505'",ROUTE)
 def test_socket_revoke_only_on_permission_change(self):self.assertIn('if(changedPermissions)',ROUTE)
 def test_ui_sends_all_three_fields_once(self):
  self.assertIn("{nickname:u.nickname||null,role:u.role,approved:u.approved}",PAGE)
  self.assertNotIn("`/admin/users/${u.id}/nickname`",PAGE)
 def test_approval_does_not_write_before_save(self):
  approval=PAGE.split('aria-label={`Stato approvazione',1)[1].split('</button>',1)[0]
  self.assertIn('setAdminUsers(old=>old.map',approval)
  self.assertNotIn("request(`/admin/users/${u.id}`",approval)
 def test_moderator_role_available(self):self.assertIn('<option value="moderator">moderator</option>',PAGE)
 def test_save_busy_disables_duplicate_submit(self):
  self.assertIn('disabled={!!u.is_primary_admin||!!adminSavingId}',PAGE)
  self.assertIn('setAdminSavingId(u.id)',PAGE)
 def test_http_atomicity_verified_against_postgresql(self):
  self.assertIn("'nickname': 'ci_first', 'role': 'presenter', 'approved': False",HTTP)
  self.assertIn('current[\'nickname\'] is None',HTTP)
 def test_http_primary_admin_immutable(self):self.assertIn("'nickname': 'other', 'role': 'platform_admin', 'approved': True",HTTP)
if __name__=='__main__':unittest.main()
