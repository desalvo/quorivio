"""RC153 source/CLI contract: permanent per-account demo, 500 true votes, recoverable editor conflict."""
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
WEB=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
SCHEMA=(ROOT/'apps/api/src/schema.sql').read_text(encoding='utf8')
SEED=(ROOT/'apps/api/src/load-test-demo.ts').read_text(encoding='utf8')
spec=importlib.util.spec_from_file_location('live_500_answers',ROOT/'tools/live_500_answers.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RC153LoadDemo(unittest.TestCase):
 def test_500_demo_is_distinct_from_original_tutorial(self):
  self.assertIn('async function provisionDemo(',API)
  self.assertIn('async function provisionLoadDemo(',API)
  self.assertIn("loadDemoPages()",API)
  self.assertIn('LOAD_DEMO_QUESTION',SEED)
  self.assertIn("'load-500-question'",SEED)
  self.assertIn("'poll'",SEED)
  self.assertIn("targetWidgetId:'load-500-question'",SEED)
  self.assertIn("'live'",SEED)
  self.assertEqual(API.count('await provisionDemo(cx,'),2)
 def test_per_account_lazy_recreation_and_atomic_deletion_reprovision(self):
  self.assertIn('demo_template_key text',SCHEMA)
  self.assertIn('uq_sessions_owner_demo_template',SCHEMA)
  self.assertIn('WHERE demo_template_key IS NOT NULL',SCHEMA)
  self.assertIn('ON CONFLICT (owner_id,demo_template_key) WHERE demo_template_key IS NOT NULL DO NOTHING RETURNING id',API)
  self.assertIn('await ensureLoadDemoForUser(auth(req)!);',API)
  self.assertIn('await provisionLoadDemo(bootstrap,uid,oid)',API)
  self.assertIn('await provisionLoadDemo(cx,uid,org.id)',API)
  self.assertIn('await provisionLoadDemo(cx,r.rows[0].id,org.organization_id)',API)
  self.assertIn("app.delete('/api/sessions/:id'",API)
  self.assertIn("if(s.demo_template_key===LOAD_DEMO_KEY)await ensureLoadDemoForUser(auth(req)!)",API)
  self.assertIn("demo_template_key:s.demo_template_key||null",API)
 def test_unpublished_default_and_no_automatic_test_or_cleanup(self):
  self.assertIn("now()+interval '365 days'",API)
  self.assertNotIn('status=\'active\'',API.split('async function provisionLoadDemo(',1)[1].split('async function ensureLoadDemoForUser',1)[0])
  self.assertNotIn('CREATE EXTENSION',SEED)
 def test_editor_conflict_suppresses_pointer_blocking_ribbon_without_disabling_other_controls(self):
  self.assertIn('suspendFormattingRibbon={pageConflict}',WEB)
  self.assertIn('active&&!ribbonDismissed&&!suspendFormattingRibbon&&widgets.some',WEB)
  self.assertIn('Confronta e riconcilia le modifiche',WEB)
  self.assertIn('editor-floating-panel.widget-selection-palette',CSS)
  broken=WEB.replace('suspendFormattingRibbon={pageConflict}', 'suspendFormattingRibbon={false}',1)
  self.assertNotIn('suspendFormattingRibbon={pageConflict}',broken)
 def test_cli_target_is_explicit_and_restricted(self):
  self.assertEqual(mod.validate_origin('https://demo.example.org','demo.example.org'),'https://demo.example.org')
  for u,h in [('http://demo.example.org','demo.example.org'),('https://x.example','demo.example.org'),
              ('https://user:pw@demo.example.org','demo.example.org'),('https://demo.example.org/evil','demo.example.org')]:
   with self.assertRaises(ValueError):mod.validate_origin(u,h)
  self.assertEqual(mod.validate_join_path('/join/0123456789abcdef'),'0123456789abcdef')
  with self.assertRaises(ValueError):mod.validate_join_path('//evil.example/join/0123456789abcdef')
 def test_cli_requires_confirmation_and_secret_from_environment(self):
  with patch.dict(os.environ,{'QUORIVIO_LOAD_PRESENTER_COOKIE':'q_auth='+'x'*40},clear=True):
   with self.assertRaises(SystemExit):mod.arguments(['--base-url','https://demo.example.org','--confirm-host','demo.example.org'])
   args=mod.arguments(['--base-url','https://demo.example.org','--confirm-host','demo.example.org','--confirm-run','--users','3','--ramp-seconds','10'])
   self.assertEqual(args.users,3)
   with self.assertRaises(SystemExit):mod.arguments(['--base-url','https://demo.example.org','--confirm-host','demo.example.org','--confirm-run','--users','500','--ramp-seconds','30'])
 def test_cli_confirms_true_server_response_delta(self):
  source=(ROOT/'tools/live_500_answers.py').read_text()
  self.assertIn("get_json(visitor,'POST',f'/api/join/{code}/activities/{aid}/widgets/{WIDGET_ID}/respond'",source)
  self.assertIn("'/api/sessions/{sid}/widget-answers'",source)
  self.assertIn('server_confirmed_new_responses',source)
  self.assertIn('delta==a.users',source)
  self.assertIn('QUORIVIO_LOAD_PRESENTER_COOKIE',source)
  self.assertNotIn('os.system(',source)
  self.assertNotIn('subprocess.',source)

if __name__=='__main__':unittest.main()
