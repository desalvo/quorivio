"""Image-reported editor/participant preview regression contracts."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[2]
UI=(R/'apps/web/src/main.tsx').read_text()
CSS=(R/'apps/web/src/style.css').read_text()

class VisualParity20261028(unittest.TestCase):
 def test_editor_can_preview_live_unsaved_draft_without_exiting(self):
  self.assertIn("className={'editor-preview-open preview-'+m}",UI)
  self.assertIn('initialPageId={designActivity}',UI)
  self.assertIn('widgets:pageWidgets',UI)
  self.assertIn('onClose={()=>setRehearsalOpen(false)}',UI)
 def test_preview_supports_native_fullscreen(self):
  self.assertIn('shellRef.current?.requestFullscreen()',UI)
  self.assertIn('document.exitFullscreen()',UI)
 def test_screenshot_bug_editor_shows_real_widget_contents(self):
  self.assertIn('canvas-widget-body-preview',UI)
  self.assertIn('<ProjectionWidgetContent sessionId={sessionId}',UI)
  self.assertIn("if(kind==='rating')",UI)
  self.assertIn("if(kind==='timer')",UI)
 def test_editor_dblclick_edits_questions_and_options_inline(self):
  self.assertIn('setEditing(w.id);requestAnimationFrame',UI)
  self.assertIn('Modifica opzione ',UI)
  self.assertIn('Aggiungi opzione di risposta',UI)
 def test_text_styles_reach_api_and_all_visual_contexts(self):
  self.assertIn('validWidgetInlineMarks(w.textMarks)',(R/'apps/api/src/domain.ts').read_text())
  self.assertIn('WidgetStyledText',UI)
  self.assertIn('widgetTypographyStyle(w.style)',UI)
  self.assertIn("textSelection.current={id:w.id,field:'label'",UI)
 def test_real_mobile_stage_retains_coordinates(self):
  self.assertIn('left:var(--stage-x)!important',CSS)
  self.assertIn('.audience-widget-layout>.page-widget[style*="--stage-x"]',CSS)
  self.assertIn('.rehearsal-stage>.rehearsal-slide',CSS)
 def test_tooltips_are_rectangles_on_both_palette_columns(self):
  self.assertIn('.editor-floating-tooltip{width:max-content',CSS)
  self.assertIn('white-space:nowrap;overflow-wrap:normal',CSS)
 def test_real_chromium_guard_is_wired_before_editor_acceptance(self):
  self.assertIn('ci_widget_visual_geometry_20261028.py',(R/'.github/workflows/ci.yml').read_text())
if __name__=='__main__':unittest.main()
