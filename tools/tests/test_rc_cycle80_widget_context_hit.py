"""RC80: editor widget right-click must never be mistaken for canvas background."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class WidgetContextHitRC80(unittest.TestCase):
    def test_widget_context_owns_event_and_cancels_background_long_press(self):
        ui = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
        self.assertIn('onContextMenu={e=>{e.preventDefault();e.stopPropagation();clearContextHold();positionMenu(e.currentTarget,e.clientX,e.clientY);', ui)
        self.assertIn("aria-label={'Azioni widget '+w.kind}", ui)
        self.assertIn('onContextMenu={e=>{if((e.target as HTMLElement).closest(".widget-canvas-item"))return;', ui)

    def test_real_browser_right_click_requires_a_hit_tested_widget_pixel(self):
        script = (ROOT / 'tools/ci_browser_editor.py').read_text(encoding='utf8')
        helper = (ROOT / 'tools/ci_editor_context_tools.py').read_text(encoding='utf8')
        self.assertIn('point=await uncovered_widget_context_point(first_widget)', script)
        self.assertIn("await page.mouse.click(point['x'],point['y'],button='right')", script)
        self.assertIn("await expect(widget_menu).to_be_visible()", script)
        self.assertIn("await expect(background_menu).to_have_count(0)", script)
        self.assertNotIn(".first.click(button='right')", script)
        self.assertIn('document.elementFromPoint(x,y)', helper)
        self.assertIn('if(hit.closest(', helper)
        self.assertIn("raise AssertionError('No real uncovered widget context pixel;", helper)

    def test_stale_background_overlay_is_dismissed_before_pointer_test(self):
        script = (ROOT / 'tools/ci_browser_editor.py').read_text(encoding='utf8')
        self.assertIn('if await background_menu.is_visible():', script)
        self.assertIn("await background_menu.get_by_role('button',name='Chiudi menu').click()", script)

    def test_early_regression_guard_runs_before_browser_acceptance(self):
        wf = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
        guard='python3 -m unittest tools.tests.test_rc_cycle80_widget_context_hit -q'
        self.assertIn(guard, wf)
        self.assertLess(wf.index(guard), wf.index('npm install --ignore-scripts'))
        self.assertIn('python3 tools/ci_browser_editor.py', wf)


if __name__ == '__main__':
    unittest.main()
