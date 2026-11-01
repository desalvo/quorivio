import pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class DemoCapacityContracts(unittest.TestCase):
 def test_demo_for_both_account_creation_flows(self):
  source=(ROOT/'apps/api/src/server.ts').read_text()
  self.assertIn('async function provisionDemo(',source)
  self.assertIn("'Quiz a tempo: scegli la seconda risposta'",source)
  self.assertIn("'Domanda aperta: cosa vorresti imparare?'",source)
  self.assertEqual(source.count('await provisionDemo(cx,'),2)
  self.assertIn("await cx.query('COMMIT')",source)
 def test_cross_replica_distinct_presence_and_live_widget(self):
  api=(ROOT/'apps/api/src/server.ts').read_text()
  ui=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn('count(DISTINCT participant_id)',api)
  self.assertIn('connected_participants:await connectedParticipants(sid)',api)
  self.assertIn('participant-count',ui)
  self.assertIn('participant-count', (ROOT/'apps/api/src/domain.ts').read_text())
 def test_load_script_is_explicitly_bounded(self):
  script=(ROOT/'tools/load_500.py').read_text()
  self.assertIn('1 <= args.users <= 500',script)
  self.assertIn("p.add_argument('--join-url'",script)
  self.assertIn("p.add_argument('--shards'",script)
  self.assertIn("p.add_argument('--source-ips'",script)
  self.assertIn("p.add_argument('--presenter-cookie'",script)
  self.assertIn("p.add_argument('--load-token'",script)
