"""Source contract for presenter-driven audience page synchronization."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class AudiencePageSyncTests(unittest.TestCase):
    def test_current_page_resolves_by_server_session_pointer(self):
        source = (ROOT / 'apps/web/src/main.tsx').read_text()
        self.assertIn('a.id===s.session.current_activity_id', source)
        self.assertIn("a.status==='open'", source)
        self.assertNotIn('activity:s.activities?.[0]||null', source)

if __name__ == '__main__':
    unittest.main()
