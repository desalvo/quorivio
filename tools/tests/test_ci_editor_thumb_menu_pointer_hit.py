"""Regression for GitHub Chromium run 40382686414 (open thumbnail menu covers its own toggle)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf-8')
BROWSER = (ROOT / 'tools/ci_browser_editor.py').read_text(encoding='utf-8')


class ThumbnailMenuPointerHit(unittest.TestCase):
    def test_trigger_above_floating_menu(self):
        self.assertRegex(CSS, r'\.page-editor-thumb-menu-trigger\{[^}]*z-index:100')
        self.assertRegex(CSS, r'\.page-editor-thumb-menu\{[^}]*z-index:80')

    def test_first_one_or_two_rows_do_not_flip_menu_up_over_trigger(self):
        # Excludes the original :nth-last-child(-n+2) selector (which matches the only page).
        self.assertIn(':nth-last-child(-n+2):not(:nth-child(-n+2)) .page-editor-thumb-menu', CSS)
        self.assertNotIn(':nth-last-child(-n+2) .page-editor-thumb-menu{top:auto;', CSS)
        self.assertIn('top:calc(100% + 8px)', CSS)
        self.assertIn('bottom:calc(100% + 8px)', CSS)

    def test_mobile_menu_is_beside_thumbnail_rail(self):
        self.assertIn('left:calc(clamp(98px,23vw,150px) + 8px)', CSS)
        self.assertIn('position:fixed', CSS)

    def test_real_chromium_checks_pointer_hit_not_only_visibility(self):
        self.assertIn('await thumb.click()',BROWSER)
        self.assertIn('Esporta layout JSON',BROWSER)
        self.assertIn('page-editor-thumb-menu-trigger',(ROOT/'apps/web/src/main.tsx').read_text())
        self.assertIn('page-editor-thumb-menu',CSS)
        self.assertNotIn('force=True',BROWSER)


if __name__ == '__main__':
    unittest.main()
