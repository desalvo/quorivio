"""RC192: source-authored results question and fully confirmed page deletion."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf8')
DELETE=(ROOT/'apps/api/src/page-deletion.ts').read_text(encoding='utf8')
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text(encoding='utf8')
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
STYLE=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
RESULTS=(ROOT/'apps/web/src/widget-results.ts').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
class SourceAndDelete(unittest.TestCase):
 def test_user_confirmation_always_calls_delete_and_discloses_detachment(self):
  block=UI.split('async function deleteCanvasPage(a:Activity)',1)[1].split('async function duplicatePage(',1)[0]
  self.assertIn('window.confirm(',block)
  self.assertIn('collegamenti presenti in altre pagine',block)
  self.assertIn('request<{ok:boolean;detached_pages:number}>',block)
  self.assertIn("'DELETE'",block)
  self.assertIn('setSnap(updated)',block)
  self.assertIn('deletion.detached_pages?',block)
 def test_atomic_server_deletion_cleans_references_and_revision(self):
  block=API.split("app.delete('/api/sessions/:id/pages/:aid'",1)[1].split('// Canvas-first pages',1)[0]
  self.assertIn('FOR UPDATE',block)
  self.assertIn('unlinkDeletedPage(reference.page_design,req.params.aid)',block)
  self.assertIn('unlinkDeletedPage(reference.result_design,req.params.aid)',block)
  self.assertIn('design_revision=design_revision+1',block)
  self.assertIn('DELETE FROM activities',block)
  self.assertIn("await cx.query('COMMIT')",block)
  self.assertIn('detached_pages:detachedPages',block)
  self.assertNotIn('page_referenced_by_session',block)
  self.assertIn('delete cleared.targetActivityId',DELETE)
  self.assertIn('delete cleared.targetWidgetId',DELETE)
  self.assertIn('delete cleared.targetQuestionId',DELETE)
 def test_option_is_strict_validated_and_keeps_legacy_default(self):
  self.assertIn('showSourceQuestion?:boolean',DOMAIN)
  self.assertIn("w.showSourceQuestion===undefined",DOMAIN)
  self.assertIn('result.showSourceQuestion!==true',RESULTS)
  self.assertIn('linkedResultQuestion(result,source)',UI)
  self.assertIn('Mostra titolo della widget collegata',UI)
  self.assertIn('Mostra risposte della widget collegata',UI)
  self.assertIn('showSourceQuestion:e.target.checked',UI)
  self.assertIn('question:'+"'"+'+questionId',UI)
 def test_live_and_rehearsal_reuse_single_results_renderer(self):
  self.assertIn('function LinkedResultSourceQuestion(',UI)
  self.assertIn('<LinkedResultSourceQuestion result={widget} source={source}/>',UI)
  self.assertIn('data-source-widget-id={source.id}',UI)
  self.assertIn('answerOptionStyle(format)',UI)
  self.assertIn("field={field('option:'+opt.id)}",UI)
  self.assertIn('className="linked-source-question"',UI)
  self.assertIn('.linked-source-answers',STYLE)
  self.assertIn('sourceWidgets} rows={rows} emptyLabel="live"',UI)
  self.assertIn('sourceWidgets} rows={rows} emptyLabel="simulazione"',UI)
 def test_does_not_publish_private_answer_keys_or_live_counts_to_audience(self):
  self.assertIn('publicPageDesign',DOMAIN)
  self.assertIn('participantVisibleWidgets(viewWidgets)',UI)
  self.assertNotIn('correctOptionIds',UI.split('function LinkedResultSourceQuestion(',1)[1].split('/** The exact same chart',1)[0])
 def test_ci_preflight_detects_breaks_before_expensive_build(self):
  self.assertIn('tools.tests.test_rc192_source_and_delete',CI)
  self.assertIn('apps/api/test/page-deletion.test.ts',CI)
  self.assertIn('apps/web/test/rc192-linked-question.test.ts',CI)
  self.assertLess(CI.index('tools.tests.test_rc192_source_and_delete'),CI.index('run: npm run build'))

if __name__=='__main__':unittest.main()
