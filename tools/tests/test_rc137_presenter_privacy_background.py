"""RC137: participant drafts and live answers never populate presenter slide fields."""
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=(ROOT/'apps/web/src/main.tsx').read_text()
UP=(ROOT/'apps/web/src/widget-asset-upload.ts').read_text()
ERRORS=(ROOT/'apps/web/src/background-upload-error.ts').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()

class RC137PresenterPrivacyAndBackground(unittest.TestCase):
 def test_live_projection_scopes_aggregates_to_authored_result_widget(self):
  projection=SRC.split('function PresenterPageResults(')[1].split('function AudienceExtensions(')[0]
  canvas=projection.split('className="projection-page-content"')[1].split('<SlideCanvasNumber')[0]
  self.assertIn('<PresenterLinkedResult sessionId={sessionId}',canvas)
  self.assertNotIn('widget-answers/detail',canvas)
  self.assertIn("w.kind==='results-button'",canvas)
  result_block=projection.split('{visible&&<div id="presenter-page-results"')[1]
  self.assertNotIn('<PresenterLinkedResult key={w.id}',result_block)
  self.assertIn('aria-expanded={visible}',projection)
  self.assertIn('onClick={()=>setVisible(v=>!v)}',projection)
 def test_rehearsal_drafts_and_choices_are_never_mirrored_into_presenter(self):
  rehearsal=SRC.split('function SessionRehearsal(')[1].split('const editorWidgetKinds=')[0]
  self.assertIn("const answer=viewer==='participant'?responses[w.id]:undefined",rehearsal)
  self.assertIn("const current=viewer==='participant'?responses[key]:undefined",rehearsal)
  self.assertIn("const sent=viewer==='participant'&&submittedAnswers[key]!==undefined",rehearsal)
  self.assertIn('<LinkedResultChart widget={w} widgets={widgets}',rehearsal)
  self.assertIn("viewer==='presenter'||!['results-button'",rehearsal)
  self.assertIn('demoResultsVisible&&<section id="rehearsal-simulated-results"',rehearsal)
  self.assertIn('setDemoResultsVisible(false)',rehearsal)
 def test_real_projection_question_parts_remain_read_only(self):
  projected=SRC.split('function ProjectedQuestionPart(')[1].split('function SlideCanvasNumber(')[0]
  self.assertIn('readOnly disabled tabIndex={-1}',projected)
  self.assertIn('type={mode===\'multiple\'?\'checkbox\':\'radio\'} disabled',projected)
  self.assertNotIn('onChange=',projected)
  self.assertNotIn('onClick=',projected)
 def test_node_only_background_error_test_is_outside_browser_typescript_sources(self):
  # apps/web/tsconfig.json includes src/ but deliberately excludes Node test types.
  # The CI runner explicitly executes all apps/web/test/*.test.ts separately.
  from json import loads
  self.assertFalse((ROOT/'apps/web/src/background-upload-error.test.ts').exists())
  node_test=ROOT/'apps/web/test/background-upload-error.test.ts'
  self.assertTrue(node_test.is_file())
  self.assertIn("'../src/background-upload-error.ts'",node_test.read_text())
  tsconfig=loads((ROOT/'apps/web/tsconfig.json').read_text())
  self.assertEqual(tsconfig['include'],['src'])
  workflow=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('node --experimental-strip-types --test apps/web/test/*.test.ts',workflow)
 def test_background_upload_reports_actual_rejection_and_never_swallows_errors(self):
  upload=SRC.split('async function uploadBackground(')[1].split('async function deleteAsset(')[0]
  self.assertIn('backgroundUploadError(r.status,code)',upload)
  self.assertIn('catch(e){notify(e);throw e}',upload)
  self.assertNotIn('return false}finally',upload)
  self.assertIn("error instanceof Error?error.message:String(error)",SRC)
  self.assertIn('invalid_upload_size',ERRORS)
  self.assertIn('image/pjpeg',UP)
  self.assertIn('.projection-results-widget-trigger',CSS)

if __name__=='__main__':unittest.main()
