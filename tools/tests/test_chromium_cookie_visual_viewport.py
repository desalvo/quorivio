"""Prevent recurrence of mobile layout-vs-visual-viewport cookie dialog failures."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]


class CookieVisualViewportRegression(unittest.TestCase):
    def test_narrow_dialog_is_anchored_to_top_not_layout_viewport_bottom(self):
        css=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
        self.assertIn('@media(max-width:740px){.functional-cookie-dialog{top:18px;bottom:auto}}',css)
        self.assertIn('.functional-cookie-dialog::backdrop',css)
        self.assertIn('max-height:calc(100dvh - 36px)',css)

    def test_both_browser_acceptances_check_actual_visual_viewport(self):
        for filename in ('ci_browser_editor.py','ci_browser_editor_postgres.py'):
            with self.subTest(script=filename):
                src=(ROOT/'tools'/filename).read_text(encoding='utf-8')
                ast.parse(src)
                self.assertIn('window.visualViewport',src)
                self.assertIn('element.getBoundingClientRect()',src)
                self.assertIn('assert visible_hit',src)
                self.assertIn('await button.click()',src)
                self.assertNotIn('force=True',src)

    def test_network_free_real_browser_regression_is_available(self):
        path=ROOT/'tools/ci_cookie_viewport.py'
        src=path.read_text(encoding='utf-8')
        ast.parse(src)
        self.assertIn('visualHeight',src)
        self.assertIn('layoutHeight',src)
        self.assertIn('inViewport',src)
        self.assertIn('is_mobile=mobile',src)
        self.assertIn('await check(browser,mobile=True)',src)


if __name__=='__main__':
    unittest.main()
