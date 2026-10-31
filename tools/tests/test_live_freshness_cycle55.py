"""RC55 source-interface checks complement actual TypeScript behavior tests."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]

class LiveFreshnessCycle55(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.transport=(ROOT/'apps/web/src/live-connection.ts').read_text()
        cls.ui=(ROOT/'apps/web/src/main.tsx').read_text()
        cls.css=(ROOT/'apps/web/src/style.css').read_text()

    def test_snapshot_freshness_is_not_reset_for_unrelated_frames(self):
        self.assertIn("message.data?.session?.id===sessionId", self.transport)
        self.assertIn("armFreshness(own);onSnapshot", self.transport)

    def test_default_freshness_window_exceeds_three_periodic_server_snapshots(self):
        self.assertIn('snapshotTimeoutMs??65000', self.transport)
        self.assertIn('const armFreshness',self.transport)

    def test_retires_stale_socket_before_close(self):
        self.assertIn("socket=null;cancelHandshake();cancelFreshness();notify('disconnected');",self.transport)
        self.assertIn('scheduleRetry();',self.transport)

    def test_error_without_close_still_retries(self):
        self.assertIn('own.onerror=()=>{if(current())retire(own)};',self.transport)

    def test_offline_dispose_and_close_clear_freshness(self):
        self.assertGreaterEqual(self.transport.count('cancelFreshness()'),4)

    def test_presenter_and_projector_consume_live_status(self):
        self.assertIn('setPresenterLive',self.ui)
        self.assertIn('createLiveConnection({',self.ui)
        self.assertIn('useLive(publicId||undefined,setPublicSnap,setScreenLive)',self.ui)
        self.assertIn('live-stale-warning',self.ui)
        self.assertIn('role="status" aria-live="polite"',self.ui)
        self.assertIn('.live-stale-warning',self.css)

    def test_score_has_no_unverified_promotion(self):
        import json
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        evidence=matrix['rc_cycle55_live_freshness_local']
        self.assertEqual(evidence['certified_score_after'],81.25)
        self.assertEqual(evidence['new_credit'],0)
        self.assertFalse(evidence['strict_rc_ready'])

if __name__=='__main__':unittest.main()
