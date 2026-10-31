"""Cycle 60 static regression: production linking revocation and CI contract."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from rc_release_preflight import preflight
from rc_gate_audit import audit


class FederatedLinkCycle60(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = (ROOT / 'apps/api/src/server.ts').read_text()
        cls.sql = (ROOT / 'apps/api/src/federated-link.ts').read_text()
        cls.schema = (ROOT / 'apps/api/src/schema.sql').read_text()
        cls.workflow = (ROOT / '.github/workflows/ci.yml').read_text()
        cls.probe = (ROOT / 'tools/ci_federated_link_postgres.mjs').read_text()

    def test_link_start_checks_signed_issue_time_and_actual_account(self):
        self.assertIn('const userId=auth(req),issuedAt=authCookieIssuedAt(req.headers.cookie)', self.s)
        self.assertEqual(self.s.count('authorizedFederatedLink(req)'), 2)
        self.assertIn('FEDERATED_LINK_ELIGIBLE_SQL', self.s)
        self.assertIn('auth_revoked_at IS NULL', self.sql)
        self.assertIn('password_changed_at IS NULL', self.sql)

    def test_both_callbacks_do_conditional_insert_and_legacy_state_fails_closed(self):
        self.assertEqual(self.s.count('validFederatedLinkIssuedAt(pending.linkIssuedAt)'), 2)
        self.assertEqual(self.s.count('db.query(FEDERATED_LINK_INSERT_SQL,[p.id,'), 2)
        self.assertIn('ON CONFLICT DO NOTHING RETURNING user_id', self.sql)
        self.assertIn('ALTER TABLE auth_flows ADD COLUMN IF NOT EXISTS link_auth_issued_at_ms bigint', self.schema)
        self.assertIn('link_auth_issued_at_ms', self.s)

    def test_disposable_postgres_acceptance_is_in_always_on_ci(self):
        self.assertIn('PostgreSQL federated identity link and revocation acceptance', self.workflow)
        self.assertIn('run: node tools/ci_federated_link_postgres.mjs', self.workflow)
        self.assertIn("QUORIVIO_CI_FEDERATED_LINK_TEST: '1'", self.workflow)
        for x in ('auth_revoked_at=now()', 'password_changed_at=now()', 'approved=false',
                  'must_change_password=true', "DELETE FROM auth_flows", 'ON CONFLICT'):
            if x == 'ON CONFLICT':
                self.assertIn(x, self.sql)
            else:
                self.assertIn(x, self.probe)
        self.assertIn("'127.0.0.1'", self.probe)
        self.assertIn('GITHUB_RUN_ID', self.probe)

    def test_rc_percentage_not_inflated_without_evidence(self):
        self.assertEqual((preflight()['score'], audit()['score']), (81.75, 81.75))
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertIn('c0fe7f7b9e41c0295387d84996a7b531b91b69a0',
                      (ROOT/'docs/COMPLETION_HANDOFF.md').read_text())
        self.assertIn('python3 tools/verify_rc_cycle59_inventory.py --historical',self.workflow)
        self.assertIn('python3 tools/verify_rc_cycle60_inventory.py',self.workflow)


if __name__ == '__main__':
    unittest.main()
