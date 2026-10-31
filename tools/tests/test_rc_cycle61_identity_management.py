"""RC61 SSO management and immutable package receipt contract tests."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class RC61Tests(unittest.TestCase):
    def test_account_scoped_routes_and_rate_limit(self):
        server=(ROOT/'apps/api/src/server.ts').read_text()
        self.assertIn("app.get('/api/auth/identities',requireAuth",server)
        self.assertIn("app.post('/api/auth/identities/unlink',requireAuth",server)
        self.assertIn('SELECT password_hash,approved,must_change_password,password_changed_at,auth_revoked_at FROM users WHERE id=$1 FOR UPDATE',server)
        self.assertIn('await bcrypt.compare(password,account.rows[0].password_hash)',server)
        self.assertIn("hash('federated-unlink:'+userId)",server)
        self.assertIn('Number(attempts.rows[0].hits)>5',server)
        sql=(ROOT/'apps/api/src/federated-identities.ts').read_text()
        self.assertIn('SELECT provider, linked_at FROM oidc_identities WHERE user_id=$1',sql)
        self.assertIn('DELETE FROM oidc_identities WHERE user_id=$1 AND provider=$2 RETURNING provider',sql)
    def test_ui_requires_password_and_offers_cancel(self):
        ui=(ROOT/'apps/web/src/main.tsx').read_text()
        for marker in ['function FederatedIdentities','Conferma scollegamento','Annulla / Cancel',"'/auth/identities/unlink','POST',{provider,password}","dashboardPage==='sso'&&<FederatedIdentities"]:
            self.assertIn(marker,ui)
    def test_ci_has_disposable_http_postgresql_acceptance(self):
        ci=(ROOT/'.github/workflows/ci.yml').read_text()
        fixture=(ROOT/'tools/ci_federated_identity_management_pg.mjs').read_text()
        self.assertIn('node tools/ci_federated_identity_management_pg.mjs',ci)
        self.assertIn("QUORIVIO_CI_FEDERATED_IDENTITIES_TEST: '1'",ci)
        self.assertIn("['localhost','127.0.0.1'].includes(url.hostname)",fixture)
        self.assertIn("assert.match(process.env.GITHUB_RUN_ID||'',/^\\d+$/",fixture)
        self.assertIn("python3 tools/verify_rc_cycle60_inventory.py --historical",ci)
        self.assertIn("python3 tools/verify_rc_cycle61_inventory.py",ci)
    def test_no_premature_gate_score(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        self.assertEqual(len(matrix['gates']),55)
        self.assertEqual(sum(g['status']=='accepted' for g in matrix['gates']),38)
        self.assertEqual(sum(g['status']=='partial' for g in matrix['gates']),17)
        self.assertEqual(next(g['status'] for g in matrix['gates'] if g['id']=='C3'),'partial')
    def test_current_manifest(self):
        subprocess.run([sys.executable,'tools/verify_rc_cycle61_inventory.py','--historical'],cwd=ROOT,check=True,capture_output=True)

if __name__=='__main__': unittest.main()
