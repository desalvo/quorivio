"""Contract for resilient, true-pointer editor context-menu access."""
import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HELPER=(ROOT/'tools/ci_editor_context_tools.py').read_text()
MOCK=(ROOT/'tools/ci_browser_editor.py').read_text()
PG=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
WF=(ROOT/'.github/workflows/ci.yml').read_text()
SMOKE=(ROOT/'tools/ci_canvas_context_hit_target_chromium.py').read_text()

class ContextCanvasVisiblePoint(unittest.TestCase):
 def test_safe_pointer_is_read_only_and_not_forced(self):
  self.assertIn('document.elementFromPoint(x, y)',HELPER)
  self.assertIn("hit.closest('.widget-canvas-item",HELPER)
  self.assertIn("canvas.scroll_into_view_if_needed()",HELPER)
  self.assertIn("await page.mouse.click(point['x'], point['y'], button='right')",HELPER)
  self.assertNotIn('force=True',HELPER+MOCK+PG)

 def test_old_fixed_corner_is_not_used_in_live_browser_fixtures(self):
  self.assertNotIn("position={'x':7,'y':7}",HELPER+MOCK+PG)
  self.assertIn('await open_canvas_context(page)',MOCK)
  self.assertIn('point=await canvas_background_point(mobile)',MOCK)
  self.assertIn('await open_canvas_context(page)',HELPER)
  self.assertIn('from ci_editor_context_tools import ensure_canvas_tools_open',PG)

 def test_preflight_is_before_live_editor_and_requires_real_hit_targets(self):
  self.assertIn('document.elementFromPoint',HELPER)
  self.assertIn('Obstructed 7px canvas corner unexpectedly accepted',SMOKE)
  self.assertIn("await canvas.click(button='right'",SMOKE)
  self.assertIn('await open_canvas_context(page)',SMOKE)
  self.assertIn('await close_canvas_tools(page)',SMOKE)
  self.assertLess(WF.index('tools/ci_canvas_context_hit_target_chromium.py'),WF.index('tools/ci_browser_editor.py'))
  for name in ('tools/ci_editor_context_tools.py','tools/ci_browser_editor.py','tools/ci_canvas_context_hit_target_chromium.py'):
   ast.parse((ROOT/name).read_text())

if __name__=='__main__':unittest.main()
