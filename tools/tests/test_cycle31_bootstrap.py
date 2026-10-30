"""Source/integration guardrails for the two-process database bootstrap acceptance."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf8')
HELPER=(ROOT/'apps/api/src/bootstrap-lock.ts').read_text(encoding='utf8')
SCRIPT=(ROOT/'tools/ci_concurrent_bootstrap_postgres.py').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class BootstrapRegression(unittest.TestCase):
    def test_schema_executes_only_under_advisory_lock(self):
        self.assertIn('await withBootstrapLock(db,async bootstrap=>{',API)
        self.assertIn('await bootstrap.query(schema)',API)
        self.assertNotIn('await db.query(schema)',API)
    def test_first_admin_and_demo_share_atomic_transaction(self):
        self.assertIn("await bootstrap.query('BEGIN')",API)
        self.assertIn('await provisionDemo(bootstrap,uid,oid)',API)
        self.assertIn("await bootstrap.query('COMMIT')",API)
        self.assertIn("await bootstrap.query('ROLLBACK')",API)
    def test_dedicated_postgres_session_not_pool_query(self):
        self.assertIn('await pool.connect()',HELPER)
        self.assertIn('pg_advisory_lock(',HELPER)
        self.assertIn('pg_advisory_unlock(',HELPER)
        self.assertIn('client.release(destroy)',HELPER)
    def test_bounded_bootstrap_wait(self):
        self.assertIn("SET lock_timeout = '120s'",HELPER)
    def test_actual_two_process_ci_acceptance(self):
        self.assertIn('postgresql://quorivio:ci-only-secret@127.0.0.1:5432/',SCRIPT)
        self.assertIn('PORTS = (19081, 19082)',SCRIPT)
        self.assertIn('1:1:1',SCRIPT)
        self.assertIn('both processes',SCRIPT)
    def test_never_use_existing_normal_db(self):
        self.assertIn("DB = 'quorivio_bootstrap_ci'",SCRIPT)
        self.assertIn('DROP DATABASE IF EXISTS',SCRIPT)
        self.assertIn('subprocess.run',SCRIPT)
        self.assertIn('capture_output=True',SCRIPT)
    def test_ci_acceptance_runs_before_primary_api(self):
        self.assertLess(CI.index('PostgreSQL 18 concurrent fresh-schema bootstrap'),CI.index('Start API against real PostgreSQL'))
    def test_new_lock_protected_section_exits_before_long_running_services(self):
        source=API.split('async function initialize(){',1)[1]
        self.assertLess(source.index('});startSessionBus('),source.index('server.listen('))

if __name__=='__main__':unittest.main()
