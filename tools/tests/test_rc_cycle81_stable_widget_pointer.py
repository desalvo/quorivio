"""RC81: real pointer acceptance must remain tied to the widget locator."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class StableWidgetPointerRC81(unittest.TestCase):
    def test_native_right_click_uses_widget_relative_offset_and_layout_stability(self):
        script=(ROOT/'tools/ci_browser_editor.py').read_text()
        helper=(ROOT/'tools/ci_editor_context_tools.py').read_text()
        self.assertIn("await first_widget.click(button='right',position=offset,trial=True)",script)
        self.assertIn("await first_widget.click(button='right',position=offset)",script)
        self.assertIn('offset_x:x-rect.left', helper)
        self.assertIn('offset_y:y-rect.top', helper)
        self.assertIn('document.elementFromPoint(x,y)',helper)
        self.assertNotIn("await page.mouse.click(point['x'],point['y'],button='right')",script)
        self.assertIn("get_by_role('group',name='Azioni widget text',exact=True)",script)
    def test_no_silent_synthetic_or_keyboard_fallback(self):
        script=(ROOT/'tools/ci_browser_editor.py').read_text()
        block=script[script.index('point=await uncovered_widget_context_point(first_widget)'):script.index("await page.keyboard.press('Escape')",script.index('point=await uncovered_widget_context_point(first_widget)'))]
        self.assertNotIn('dispatch_event(',block)
        self.assertNotIn('Shift+F10',block)
        self.assertIn('canvas_background_menu_open=',block)
        self.assertIn('await expect(background_menu).to_have_count(0)',block)
    def test_early_gate_before_expensive_npm_and_real_chromium(self):
        wf=(ROOT/'.github/workflows/ci.yml').read_text()
        test='python3 -m unittest tools.tests.test_rc_cycle81_stable_widget_pointer -q'
        self.assertIn(test,wf)
        self.assertLess(wf.index(test),wf.index('npm ci --ignore-scripts'))
        self.assertIn('python3 tools/ci_browser_editor.py',wf)

if __name__=='__main__': unittest.main()
