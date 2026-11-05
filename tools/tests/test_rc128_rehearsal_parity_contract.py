"""RC128: enforce the screenshot-driven editor/rehearsal correction contract."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
JSX=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
TYPO=(ROOT/'apps/web/src/stage-widget-typography.ts').read_text()

class RehearsalParityContracts(unittest.TestCase):
 def test_no_presenter_free_text_demo_under_question(self):
  self.assertNotIn('rehearsal-presenter-free-text" aria-label="Risposte libere nella simulazione',JSX)
  self.assertIn("viewer==='presenter'?'Invia risposta':'Invia risposta di prova'",JSX)
  self.assertIn("kind==='results-button'?(()=>{",JSX)
  self.assertIn('linkedStatisticContext(w,viewActivity,activities,viewWidgets)',JSX)
  self.assertIn('demoResultsVisible&&<section id="rehearsal-simulated-results"',JSX)
 def test_preview_preserves_authored_geometry_and_fonts(self):
  self.assertIn("'--stage-width':`${w.position?.width??45}%`",JSX)
  self.assertIn('stageWidgetTypography(w,{pageTitle:viewActivity.title,masterTitleStyle:snapshot.session.theme?.master?.titleStyle},mobile)',JSX)
  self.assertIn("'--authored-widget-font-size':typography.fontSize",TYPO)
  self.assertIn('widgetTypographyStyle(resolved)',TYPO)
  self.assertIn('font-size:var(--authored-widget-font-size,1.25cqw)!important;',CSS)
  self.assertNotIn('style={display.style as React.CSSProperties}',JSX)
 def test_resize_input_and_no_reflow_for_dual_preview(self):
  self.assertIn('function EditorAnswerFieldPreview(',JSX)
  self.assertIn('onHeightChange={height=>patch(w.id',JSX)
  self.assertIn('.rehearsal-pane>.rehearsal-slide>.rehearsal-widgets',CSS)
 def test_state_restoration_is_auth_checked(self):
  self.assertIn('workspaceRestore=useRef(readWorkspaceLocation())',JSX)
  self.assertIn("snap.session.id!==selected",JSX)
  self.assertIn('writeWorkspaceLocation({sessionId:\'\',section:\'workspace\'',JSX)
 def test_collisions_sweep_replaces_jumpback_on_drag(self):
  self.assertIn('moveWidgetsToCollisionLimit(base,ids',JSX)
  self.assertIn('setAlignmentGuides(accepted.find',JSX)

if __name__=='__main__':unittest.main()
