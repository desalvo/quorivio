"""Static guarantees for CI's real-database boot smoke gate."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class CiIntegrationTests(unittest.TestCase):
    def test_postgres_service_and_live_boot_smoke(self):
        flow = (ROOT / '.github/workflows/ci.yml').read_text()
        for token in ('postgres:18-alpine', 'Start API against real PostgreSQL',
                      'api/health/ready', 'api/health/live', 'Assert database bootstrapping',
                      'widget_answers', 'auth_flows', 'api_rate_windows'):
            self.assertIn(token, flow)

    def test_converter_build_and_scan_are_gated(self):
        flow = (ROOT / '.github/workflows/ci.yml').read_text()
        self.assertIn('file: Dockerfile.converter', flow)
        self.assertIn('quorivio-converter:gate', flow)
        self.assertIn('image-ref: quorivio:gate', flow)
        self.assertIn('needs: [validate, image-build]', flow)

    def test_password_reset_throttle_is_shared(self):
        server = (ROOT / 'apps/api/src/server.ts').read_text()
        self.assertNotIn('resetRequests=new Map', server)
        self.assertIn('password-reset:', server)
        self.assertIn('INSERT INTO api_rate_windows(client_hash,bucket,hits)', server)

if __name__ == '__main__': unittest.main()

class LiveCiIntegrationTests(unittest.TestCase):
    def test_live_postgresql_e2e_is_mandatory_and_follows_password_change(self):
        flow = (ROOT / '.github/workflows/ci.yml').read_text()
        self.assertIn('PostgreSQL-backed concurrent live lifecycle E2E', flow)
        self.assertIn('python3 tools/ci_live_http.py', flow)
        self.assertLess(flow.index('python3 tools/ci_portable_http.py'), flow.index('python3 tools/ci_live_http.py'))
        self.assertLess(flow.index('python3 tools/ci_live_http.py'), flow.index('Stop integration API'))

    def test_live_smoke_covers_concurrency_idempotency_privacy_and_timer(self):
        script = (ROOT / 'tools/ci_live_http.py').read_text()
        for required in ('ThreadPoolExecutor', 'range(24)', 'already_submitted',
                         "row['valid'] == 24", "'pseudonym' not in", 
                         "'timed_quiz'", "time.sleep(5.3)", "timed_row['valid'] == 1"):
            self.assertIn(required, script)
