"""Regression checks for page-order request serialization in the editor."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PageOrderInflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'apps/web/src/main.tsx').read_text()

    def test_page_reordering_is_serialized(self):
        self.assertIn('const pageOrderRequestInFlight=useRef(false)', self.source)
        self.assertIn('if(pageOrderRequestInFlight.current)return;', self.source)
        self.assertIn('pageOrderRequestInFlight.current=true;', self.source)
        self.assertIn('finally{pageOrderRequestInFlight.current=false;setPageOrderPending(false)}', self.source)

    def test_stale_session_response_not_applied(self):
        self.assertIn('if(selectedSessionRef.current===sessionId){', self.source)
        self.assertIn('setSnap(outcome.snapshot)', self.source)
        self.assertIn('snapshot=>snapshot.activities.map(activity=>activity.id)', self.source)

    def test_filmstrip_disabled_during_order_change(self):
        self.assertIn('aria-busy={pageOrderPending}', self.source)
        self.assertIn("draggable={snap.session.status!=='closed'&&!pageOrderPending}", self.source)

if __name__ == '__main__':
    unittest.main()
