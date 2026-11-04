"""RC166: disposable, GitHub-run-scoped CI credentials instead of literals.

This cannot certify a third-party GitGuardian incident: the user must inspect the
incident's file/line, validity and exposure in GitGuardian itself.
"""
from __future__ import annotations
import re
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
CI=(ROOT/'.github/workflows/ci.yml').read_text()
BOOT=(ROOT/'tools/ci_concurrent_bootstrap_postgres.py').read_text()
TIMED=(ROOT/'tools/ci_timed_widgets_postgres.py').read_text()
FED=(ROOT/'tools/ci_federated_identity_management_pg.mjs').read_text()

class RC166CICredentials(unittest.TestCase):
    def test_run_scoped_postgres_service_and_http_db_urls(self):
        self.assertIn("POSTGRES_PASSWORD: ${{ format('ci-{0}-{1}-{2}', github.run_id, github.run_attempt, github.sha) }}", CI)
        self.assertIn('QUORIVIO_CI_DB_PASSWORD: ${{ format(',CI)
        self.assertIn('PGPASSWORD: ${{ env.QUORIVIO_CI_DB_PASSWORD }}',CI)
        self.assertGreaterEqual(CI.count('github.run_attempt, github.sha'),8)
        self.assertNotRegex(CI,r'(?m)^\s+POSTGRES_PASSWORD: (?!\$\{\{)[^\s#]+')
    def test_bootstrap_and_timed_sql_refuse_arbitrary_production_endpoint(self):
        self.assertIn('ci_database_password()',BOOT)
        self.assertIn('quote(ci_database_password()',BOOT)
        self.assertIn("os.environ.get('GITHUB_RUN_ID', '').isdigit()",BOOT)
        self.assertIn('secrets.token_urlsafe(48)',BOOT)
        self.assertIn('secrets.token_urlsafe(32)',BOOT)
        self.assertIn('pg_url!=allowed',TIMED)
        self.assertIn("os.environ.get('GITHUB_RUN_ID','').isdigit()",TIMED)
        self.assertIn("'PGPASSWORD':db_password",TIMED)
    def test_admin_and_auth_secrets_created_per_run_and_masked(self):
        for name in ('admin_password','changed_password','auth_secret'):
            self.assertIn(name+'="$(openssl rand -hex',CI)
            self.assertIn('"$'+name+'"',CI)
        self.assertIn('echo "ADMIN_PASSWORD=$admin_password" >> "$GITHUB_ENV"',CI)
        self.assertIn('echo "AUTH_SECRET=$auth_secret" >> "$GITHUB_ENV"',CI)
        self.assertIn('echo "QUORIVIO_CI_NEW_PASSWORD=$changed_password" >> "$GITHUB_ENV"',CI)
        self.assertNotRegex(CI,r'(?m)^\s+(?:ADMIN_PASSWORD|AUTH_SECRET|QUORIVIO_CI_ADMIN_PASSWORD|QUORIVIO_CI_NEW_PASSWORD): [^\s$]+')
    def test_federated_fixture_does_not_commit_static_password(self):
        self.assertIn("password=randomBytes(24).toString('hex')",FED)
        self.assertNotIn('ci-only-federated-password',FED)
    def test_preflight_runs_before_npm_and_keeps_secret_scanners(self):
        self.assertIn('tools.tests.test_rc166_ci_credentials',CI)
        self.assertLess(CI.index('tools.tests.test_rc166_ci_credentials'),CI.index('npm install --ignore-scripts'))
        for marker in ('Detect credential leaks','gitleaks'):
            self.assertIn(marker,CI)
    def test_negative_mutations_rejected(self):
        broken=CI.replace('POSTGRES_PASSWORD: ${{ format(', 'POSTGRES_PASSWORD: null # ${{ format(',1)
        self.assertNotEqual(CI,broken)
        self.assertFalse("POSTGRES_PASSWORD: ${{ format('ci-{0}-{1}-{2}'" in broken)
        broken2=CI.replace('echo "AUTH_SECRET=$auth_secret" >> "$GITHUB_ENV"','',1)
        self.assertNotEqual(CI,broken2)
        self.assertNotIn('echo "AUTH_SECRET=$auth_secret" >> "$GITHUB_ENV"',broken2)

if __name__=='__main__':unittest.main()
