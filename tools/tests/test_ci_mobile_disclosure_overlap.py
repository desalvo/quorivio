"""Regression contracts for CI 40510491774's mobile accessible-summary overlay."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class MobileDisclosureOverlapRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui=(ROOT/'apps/web/src/main.tsx').read_text()
        cls.css=(ROOT/'apps/web/src/style.css').read_text()
        cls.editor=(ROOT/'tools/ci_browser_editor.py').read_text()
        cls.real=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
        cls.preflight=(ROOT/'tools/ci_accessible_disclosure_chromium.py').read_text()
        cls.workflow=(ROOT/'.github/workflows/ci.yml').read_text()

    def test_accessible_disclosure_dismisses_contextual_toolbar(self):
        self.assertIn('onToggle={e=>{if(e.currentTarget.open)setBackgroundMenu(false)}}',self.ui)

    def test_collapsed_summary_above_contextual_overlay_but_released_when_open(self):
        self.assertIn('.canvas-accessible-controls:not([open]){position:relative;z-index:52}',self.css)
        self.assertIn('.canvas-accessible-controls[open]{position:relative;z-index:auto}',self.css)
        self.assertIn('z-index:48!important',self.css)

    def test_mobile_browser_asserts_real_hit_target_and_closed_toolbar(self):
        self.assertIn("await page.set_viewport_size({'width':420,'height':860})",self.editor)
        self.assertIn("get_by_role('complementary',name='Aggiungi widget')",self.editor)
        self.assertNotIn('force=True',self.editor)

    def test_postgresql_browser_closes_popup_before_accessible_alternative(self):
        self.assertIn('await edit_canvas_widget_title(widgets,',self.real)
        self.assertIn("await expect(editor.get_by_text('Conflitto di revisione'))",self.real)
        self.assertNotIn('force=True',self.real)

    def test_preflight_uses_actual_css_and_reproduces_overlap(self):
        self.assertIn("apps/web/src/style.css",self.preflight)
        self.assertIn('assert overlap',self.preflight)
        self.assertIn('elementFromPoint',self.preflight)
        self.assertIn('await check.check()',self.preflight)
        self.assertIn("QUORIVIO_CHROMIUM_PATH",self.preflight)

    def test_ci_runs_real_browser_overlap_preflight_before_editor(self):
        self.assertLess(self.workflow.index('tools/ci_accessible_disclosure_chromium.py'),self.workflow.index('tools/ci_browser_editor.py'))
        self.assertNotIn('playwright install --with-deps chromium',self.workflow)

if __name__=='__main__':unittest.main()
