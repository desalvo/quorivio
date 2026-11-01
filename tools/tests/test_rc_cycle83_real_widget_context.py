"""RC83: Chromium observed canvas background menu for a genuine widget right-click.

This guard checks production event capture, the geometry fallback, and that the
real Playwright pointer test continues to fail if the widget menu is absent.
"""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class RealWidgetContextRC83(unittest.TestCase):
 def test_canvas_capture_centrally_routes_context_to_widget_or_background(self):
  s=(ROOT/'apps/web/src/main.tsx').read_text()
  for required in (
   'onContextMenuCapture={handleCanvasContext}',
   'const widget=direct&&canvas.contains(direct)?direct:canvasWidgetAtPoint(canvas,e.clientX,e.clientY)',
   'openWidgetContextMenu(widgetId,widget,e.clientX,e.clientY)',
   'clearContextHold();openBlankMenu()',
   'data-widget-id={w.id}',
   'e.preventDefault();e.stopPropagation();',
  ):self.assertIn(required,s)
  self.assertIn('canvasWidgetAtPoint', (ROOT/'apps/web/src/editor-context-hit.ts').read_text())

 def test_native_browser_action_and_fail_closed_menu_assertions_remain(self):
  t=(ROOT/'tools/ci_browser_editor.py').read_text()
  self.assertIn("await first_widget.click(button='right',position=offset)",t)
  self.assertIn("await expect(widget_menu).to_be_visible(timeout=4000)",t)
  self.assertIn('canvas_background_menu_open=',t)
  self.assertIn('await expect(background_menu).to_have_count(0)',t)
  self.assertNotIn('dispatch_event(',t)

 def test_early_production_capture_gate(self):
  wf=(ROOT/'.github/workflows/ci.yml').read_text()
  guard='python3 -m unittest tools.tests.test_rc_cycle83_real_widget_context -q'
  self.assertIn(guard,wf)
  self.assertLess(wf.index(guard),wf.index('npm install --ignore-scripts'))

if __name__=='__main__':unittest.main()
