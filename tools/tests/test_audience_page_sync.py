"""Source contract for presenter-driven audience page synchronization."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class AudiencePageSyncTests(unittest.TestCase):
    def test_current_page_resolves_by_server_session_pointer(self):
        source = (ROOT / 'apps/web/src/main.tsx').read_text()
        helper = (ROOT / 'apps/web/src/participant-state.ts').read_text()
        self.assertIn('publicActivityFromSnapshot(s)', source)
        self.assertIn('snapshot.session.current_activity_id', helper)
        self.assertIn("a?.id===id&&a.status==='open'", helper)
        self.assertIn("snapshot?.session?.status!=='active'", helper)
        self.assertNotIn('activity:s.activities?.[0]||null', source)

if __name__ == '__main__':
    unittest.main()
