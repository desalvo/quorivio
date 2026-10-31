"""Structural regressions for shared, view-isolated WebSocket fanout.

Detailed runtime and 501-socket tests live in apps/api/test/live-broadcast-cycle57.test.ts.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class LiveFanoutCycle57(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=(ROOT/'apps/api/src/server.ts').read_text()
        cls.fanout=(ROOT/'apps/api/src/live-broadcast.ts').read_text()
        cls.workflow=(ROOT/'.github/workflows/ci.yml').read_text()

    def test_initial_snapshot_uses_the_authoritative_queue(self):
        self.assertIn('void broadcastLocal(sid).catch(',self.server)
        self.assertNotIn('snapshot(sid).then(data=>',self.server)
        self.assertIn('createLiveSnapshotQueue',self.server)

    def test_separate_presenter_and_participant_payloads(self):
        self.assertIn("const ownerPayload = presenter.length ? JSON.stringify",self.fanout)
        self.assertIn("const audiencePayload = audience.length ? JSON.stringify",self.fanout)
        self.assertIn('audienceView(data)',self.fanout)
        self.assertIn('participantSnapshot,ws=>',self.server)

    def test_slow_client_and_transport_faults_are_scoped_to_client(self):
        self.assertIn('shouldDropSlowSocket(client.bufferedAmount, size)',self.fanout)
        self.assertIn("client.close(1013, 'slow_consumer')",self.fanout)
        self.assertIn("client.close(1011, 'transport_error')",self.fanout)

    def test_historical_inventory_preserved_and_new_one_is_current(self):
        self.assertTrue((ROOT/'docs/validation/RC_CYCLE56_PACKAGE_INVENTORY_20261030.json').exists())
        self.assertTrue((ROOT/'tools/verify_rc_cycle56_inventory.py').exists())
        self.assertIn('python3 tools/verify_rc_cycle56_inventory.py --historical',self.workflow)
        self.assertIn('python3 tools/verify_rc_cycle57_inventory.py --historical',self.workflow)
        self.assertIn('python3 tools/verify_rc_cycle61_inventory.py',self.workflow)

    def test_maintainer_only_commit_and_unchanged_verified_gate(self):
        # The latest RC status is prepended each cycle: historic evidence must
        # not disappear simply because it moves beyond an arbitrary prefix.
        text=(ROOT/'docs/DEVELOPMENT_STATUS.it.md').read_text()
        receipt=(ROOT/'docs/RC58_VERIFIED_IDLE_SLO_AND_REFRESH.it.md').read_text()
        self.assertIn('c0fe7f7b9e41c0295387d84996a7b531b91b69a0',receipt)
        self.assertRegex(text.split('\n---\n',1)[0],r'8[2-9],\d{2}%')
        self.assertIn('# Quorivio 0.1.0-dev — ciclo 58:',text)

if __name__=='__main__':unittest.main()
