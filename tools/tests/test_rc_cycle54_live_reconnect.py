"""Browser WebSocket resilience acceptance contracts for cycle 54."""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
SRC=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
CLIENT=(ROOT/'apps/web/src/live-connection.ts').read_text(encoding='utf-8')
TEST=(ROOT/'apps/web/test/live-connection-cycle54.test.ts').read_text(encoding='utf-8')

class LiveRecoveryCycle54(unittest.TestCase):
 def test_shared_by_both_react_screens(self):
  self.assertIn('createLiveConnection({',SRC)
  self.assertEqual(SRC.count('useLive('),4)  # one definition + presenter, public and participant
  self.assertIn('updateRef.current(s as Snapshot)',SRC)
  self.assertIn('connectionRef.current?.(state)',SRC)

 def test_stale_socket_is_fenced_before_disposal_and_timeout(self):
  self.assertIn('socket===own',CLIENT)
  self.assertIn('socket=null;cancelHandshake()',CLIENT)
  self.assertIn('previous?.close()',CLIENT)
  self.assertIn('if(!current())return',CLIENT)

 def test_privacy_requires_correct_session(self):
  self.assertIn('message.data?.session?.id===sessionId',CLIENT)
  self.assertIn("message?.type==='snapshot'",CLIENT)
  self.assertNotIn('console.log(',CLIENT)

 def test_terminal_policy_closes_do_not_reconnect(self):
  self.assertIn('event.code===4003||event.code===1008',CLIENT)
  self.assertIn("notify('blocked')",CLIENT)
  self.assertIn('if(!disposed&&!terminal',CLIENT)
  self.assertIn("blocked:'Accesso live non autorizzato",SRC)

 def test_retry_handshake_and_offline_are_bounded(self):
  self.assertIn('nextLiveRetryMs(attempt)',CLIENT)
  self.assertIn('Math.min(30000',CLIENT)
  self.assertIn('options.handshakeTimeoutMs??15000',CLIENT)
  self.assertIn('cancelRetry();cancelHandshake();',CLIENT)
  self.assertIn('window.addEventListener(\'online\'',SRC)
  self.assertIn('window.addEventListener(\'offline\'',SRC)

 def test_deterministic_race_coverage(self):
  for scenario in ('network outage fences previous socket', 'a stuck handshake is abandoned',
   'server authorization close codes', 'error of a retired socket',
   'disposed transport cancels pending timers', 'socket construction failure', 'loading a live page while already offline'):
   self.assertIn(scenario,TEST)

 def test_rc_remains_conservative(self):
  g=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  self.assertEqual(g['rc_cycle54_live_reconnect_local_20261030']['new_credit'],0)
  self.assertEqual(len(g['gates']),55)
  self.assertEqual(sum(x['weight']*(1 if x['status']=='accepted' else 0.5 if x['status']=='partial' else 0) for x in g['gates']),81.75)

 def test_historical_manifest_and_current_verifier_in_ci(self):
  workflow=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('python3 tools/verify_rc_cycle53_inventory.py --historical',workflow)
  self.assertIn('python3 tools/verify_rc_cycle54_inventory.py',workflow)
  self.assertTrue((ROOT/'docs/validation/RC_CYCLE53_PACKAGE_INVENTORY_20261030.json').is_file())

if __name__=='__main__':unittest.main()
