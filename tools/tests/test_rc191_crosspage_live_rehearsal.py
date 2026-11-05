"""RC191: verify shared cross-page results and independent dual rehearsal routing.

The legacy single-page preview used a local source lookup and never followed
presenterHidden/audiencePageId. Fast fail-closed CI guards prevent regressions
before the expensive browser/PostgreSQL stages.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
RESULTS=(ROOT/'apps/web/src/widget-results.ts').read_text(encoding='utf8')
ROUTES=(ROOT/'apps/web/src/rehearsal-page-routing.ts').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class CrossPageRehearsal(unittest.TestCase):
 def test_live_reads_only_the_linked_source_activity_and_never_cancels_on_snapshot_updates(self):
  code=UI.split('function PresenterLinkedResult(',1)[1].split('function ProjectedQuestionPart(',1)[0]
  self.assertIn('linkedStatisticContext(widget,activity,activities,widgets)',code)
  self.assertIn('const sourceActivityId=context?.activity.id||activity.id',code)
  self.assertIn('widget-answers/detail?activity_id=${encodeURIComponent(sourceActivityId)}',code)
  self.assertIn('window.setInterval(()=>void load(),3000)',code)
  self.assertIn('data-source-activity-id={context?.activity.id',code)
  self.assertNotIn('liveRevision',code)
  self.assertIn('Risultati temporaneamente non disponibili',code)
  self.assertNotIn('response_payload',code)
 def test_rehearsal_renders_distinct_presenter_and_audience_page_widgets(self):
  code=UI.split('function SessionRehearsal(',1)[1].split('const editorWidgetKinds',1)[0]
  self.assertIn('rehearsalPresenterPages(activities)',code)
  self.assertIn('rehearsalAudiencePage(activity,activities)',code)
  self.assertIn("viewer==='presenter'?activity:audienceActivity",code)
  self.assertIn("viewer==='presenter'?presenterWidgets:widgets",code)
  self.assertIn('linkedStatisticContext(w,viewActivity,activities,viewWidgets)',code)
  self.assertIn('presenterPages.length-1',code)
  self.assertIn('height={participantPhoneLayout(widgets,audienceActivity?.page_design?.mobile).height}',code)
  self.assertNotIn('const activity=activities[page]',code)
  self.assertNotIn('linkedStatisticSource(w,widgets)',code)
 def test_hidden_page_and_foreign_page_does_not_leak_to_presenter(self):
  self.assertIn('presenterVisiblePages(pages)',ROUTES)
  self.assertIn('presenter.page_design?.audiencePageId',ROUTES)
  self.assertIn('pages.find(page=>page.id===target)',ROUTES)
  self.assertIn('linkedStatisticActivity(widget,current,activities)',RESULTS)
  self.assertIn('linkedStatisticSource(widget,widgets)',RESULTS)
  self.assertIn('if(!activity)return undefined',RESULTS)
  self.assertIn('return source?{activity,widgets,source}:undefined',RESULTS)
 def test_does_not_weaken_public_aggregate_privacy_or_authorized_source_api(self):
  api=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf8')
  self.assertIn("app.get('/api/sessions/:id/widget-answers/detail',requireAuth",api)
  self.assertIn('const s=await owner(req.params.id,auth(req)!)',api)
  self.assertIn('aggregateWidgetAnswerRevisions(r.rows)',api)
  self.assertIn('participantVisibleWidgets(viewWidgets)',UI)
  self.assertIn('participantPhoneLayout(viewWidgets,viewActivity?.page_design?.mobile).widgets',UI)
 def test_ci_early_preflight_and_complete_build_stay_mandatory(self):
  self.assertIn('tools.tests.test_rc191_crosspage_live_rehearsal',WORKFLOW)
  self.assertIn('apps/web/test/rc191-cross-page-preview.test.ts',WORKFLOW)
  self.assertIn('run: npm run build',WORKFLOW)
  self.assertLess(WORKFLOW.index('tools.tests.test_rc191_crosspage_live_rehearsal'),WORKFLOW.index('run: npm run build'))
 def test_negative_mutation_detects_old_single_page_preview(self):
  modified=UI.replace('linkedStatisticContext(w,viewActivity,activities,viewWidgets)','linkedStatisticSource(w,viewWidgets)')
  self.assertNotIn('linkedStatisticContext(w,viewActivity,activities,viewWidgets)',modified)
  modified=ROUTES.replace('return presenterVisiblePages(pages)','return [...pages]')
  self.assertNotIn('return presenterVisiblePages(pages)',modified)

if __name__=='__main__':unittest.main()
