"""RC56 integration and evidence contracts: no fictitious idle-session heartbeat."""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]

class LiveHeartbeatCycle56(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api=(ROOT/'apps/api/src/server.ts').read_text()
        cls.pump=(ROOT/'apps/api/src/live-periodic-refresh.ts').read_text()
        cls.browser=(ROOT/'apps/web/src/live-connection.ts').read_text()

    def test_server_sends_periodic_authoritative_snapshot_not_empty_ping(self):
        self.assertIn('const livePeriodicRefresh=createLivePeriodicRefresh(',self.api)
        self.assertIn('readAndSend:broadcastLocal',self.api)
        self.assertRegex(self.api,r'setInterval\(\(\)=>\{void livePeriodicRefresh\.tick\(\)\},20000\)')
        self.assertIn('periodicLiveSnapshots.unref()',self.api)
        self.assertIn('if(!sockets.get(sid)?.size)return',self.api)

    def test_refresh_never_causes_fanout_per_client_or_cross_replica_notifies(self):
        self.assertIn('activeSessions:()=>sockets.keys()',self.api)
        self.assertIn('const inFlight = new Set<string>()',self.pump)
        self.assertIn('if (running) return;',self.pump)
        self.assertIn('inFlight.add(sessionId)',self.pump)
        self.assertNotIn('pg_notify',self.pump)
        self.assertNotIn('sockets.values()',self.pump)

    def test_watchdog_does_not_accept_incorrect_session_or_missing_snapshots(self):
        self.assertIn("message?.type==='snapshot'&&message.data?.session?.id===sessionId",self.browser)
        self.assertIn('snapshotTimeoutMs??65000',self.browser)
        self.assertIn('onSnapshot(message.data)',self.browser)
        self.assertIn('catch (error)',self.pump)

    def test_new_local_work_does_not_falsely_promote_certified_progress(self):
        m=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        self.assertEqual(m['rc_cycle56_authoritative_idle_snapshots_local']['new_credit'],0)
        self.assertEqual(m['rc_cycle56_authoritative_idle_snapshots_local']['certified_rc'],81.25)
        self.assertFalse(m['rc_cycle56_authoritative_idle_snapshots_local']['remote_ci_verified'])

    def test_current_cumulative_handoff_includes_uncommitted_cycles(self):
        d=(ROOT/'docs/COMPLETION_HANDOFF.md').read_text()
        self.assertIn('cycles 49–56',d)
        self.assertIn('64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c',d)
        self.assertRegex(d[:1300],r'8[2-9]\.\d{2}%')

if __name__=='__main__':unittest.main()
