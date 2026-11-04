"""RC164: prevent browser palette enumeration from hiding graphic preset triggers."""
from __future__ import annotations
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BROWSER=(ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf8')
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

def accepts_graphic_palette(browser: str, ui: str) -> bool:
    return all(x in browser for x in (
        'e.dataset.widgetKind || e.dataset.graphicPalette',
        "graphics=palette.locator('button.editor-icon-tool[data-graphic-palette]')",
        "for kind,label in [('line','Linee'),('shape','Forme')]",
        "await graphic.click(button='right')",
        "await expect(popup).to_be_visible()",
        "await page.keyboard.press('Escape')",
        'e.dataset.graphicPalette || !e.hasAttribute("title")',
    )) and all(x in ui for x in (
        "className={schema?'slide-scheme-graphic-trigger':'editor-icon-tool'}",
        'data-graphic-palette={kind}',
        "'Aggiungi widget: '+label",
        'onContextMenu={e=>{e.preventDefault()',
        '''role="dialog" aria-label={'Scegli '+label.toLowerCase()+' da inserire'}''',
        'GRAPHIC_PRESETS[kind].map',
    ))

class RC164GraphicPaletteChromium(unittest.TestCase):
    def test_existing_graphic_triggers_are_visible_to_chromium_catalog(self):
        self.assertTrue(accepts_graphic_palette(BROWSER,UI))
        self.assertIn("required={'rating','reactions','text','shape','line'",BROWSER)
        self.assertIn("assert len(kinds)==len(set(kinds))",BROWSER)
        self.assertIn("assert len(labels)==len(set(labels))",BROWSER)
        self.assertIn("assert all(names) and len(set(names))==len(names)",BROWSER)
    def test_user_right_click_opens_preset_picker_without_inserting(self):
        self.assertIn("await graphic.click(button='right')",BROWSER)
        self.assertIn("await popup.locator('.graphic-preset-choices button').count()>=2",BROWSER)
        self.assertIn("await expect(popup).to_have_count(0)",BROWSER)
        self.assertIn("onClick={()=>{if(suppressClick.current)",UI)
    def test_negative_regression_old_widgetkind_only_cannot_pass(self):
        bad=BROWSER.replace('e.dataset.widgetKind || e.dataset.graphicPalette','e.dataset.widgetKind',1)
        self.assertFalse(accepts_graphic_palette(bad,UI))
    def test_negative_missing_context_menu_cannot_pass(self):
        bad=BROWSER.replace("await graphic.click(button='right')","await graphic.click()",1)
        self.assertFalse(accepts_graphic_palette(bad,UI))
    def test_negative_missing_graphic_trigger_cannot_pass(self):
        bad=UI.replace('data-graphic-palette={kind}','data-graphic-style={kind}',1)
        self.assertFalse(accepts_graphic_palette(BROWSER,bad))
    def test_ci_runs_preflight_before_expensive_browser_and_current_inventory(self):
        self.assertIn('test_rc164_graphic_palette_chromium_contract',WORKFLOW)
        self.assertIn('python3 tools/ci_browser_editor.py',WORKFLOW)
        self.assertIn('verify_rc_cycle163_inventory.py --historical',WORKFLOW)
        self.assertIn('verify_rc_cycle164_inventory.py',WORKFLOW)
        self.assertLess(WORKFLOW.index('test_rc164_graphic_palette_chromium_contract'),WORKFLOW.index('npm run build'))

if __name__=='__main__':unittest.main()
