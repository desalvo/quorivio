"""RC224 early preflight: viewport-safe thumbnail actions and Arial defaults."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT/'apps/web/src/main.tsx').read_text()
CSS = (ROOT/'apps/web/src/style.css').read_text()
LAYOUT = (ROOT/'apps/web/src/thumbnail-menu-layout.ts').read_text()
TYPO = (ROOT/'apps/web/src/widget-typography-defaults.ts').read_text()
MASTER = (ROOT/'apps/web/src/slide-master.ts').read_text()
WORKFLOW = (ROOT/'.github/workflows/ci.yml').read_text()

def validate(ui=UI,css=CSS,layout=LAYOUT,typo=TYPO,master=MASTER,workflow=WORKFLOW):
    required={
        'UI': (ui, ["setPageMenuPosition(thumbnailMenuPosition(", 'maxHeight:pageMenuPosition.maxHeight',
                    'className="page-editor-thumb-submenu"', '<summary>Crea e importa pagine</summary>',
                    '<summary>Ordina pagine</summary>', '<summary>Esporta e dati</summary>',
                    "Rinomina {selectedPageIds.length>1?", "Elimina {selectedPageIds.length>1?",
                    'style:{...initialWidgetTextStyle(kind)', 'style:{...initialWidgetTextStyle(k)',
                    "[newTitleWidget(snap.session.title),newFooterWidget('schema-footer')]"]),
        'CSS': (css, ['.page-editor-thumb-menu-floating .page-editor-thumb-submenu>summary:focus-visible',
                      'min-height:0!important;overflow-x:hidden!important;overflow-y:auto!important;',
                      'max-height:var(--thumbnail-menu-max-height,calc(100dvh - 16px))!important;',
                      ':is(.slide-scheme-workspace,.powerpoint-editor) .widget-canvas-item']),
        'LAYOUT': (layout, ['export function thumbnailMenuPosition(', 'viewportHeight-top-pad', 'const preferredHeight=Math.min(340,availableHeight)']),
        'TYPO': (typo, ["return widgetTextDefaults(kind,{fontFamily:'Arial'})||{fontFamily:'Arial'}"]),
        'MASTER': (master,["export const DEFAULT_TITLE_STYLE={fontFamily:'Arial'", "export const DEFAULT_FOOTER_STYLE={fontFamily:'Arial'", "const style=w.kind==='title'?{...DEFAULT_TITLE_STYLE"]),
        'WORKFLOW': (workflow, ['tools.tests.test_rc224_thumbnail_arials', 'apps/web/test/rc224-thumbnail-menu-arial.test.ts',
                               'tools/ci_rc224_thumbnail_menu_chromium.py']),
    }
    for location,(code,markers) in required.items():
        for mark in markers:
            if mark not in code:raise AssertionError(f'{location}: {mark}')

class RC224ThumbnailArial(unittest.TestCase):
    def test_viewport_menu_and_every_arial_factory(self):validate()
    def test_no_uncapped_menu_position(self):
        with self.assertRaises(AssertionError):validate(layout=LAYOUT.replace('viewportHeight-top-pad', 'viewportHeight-pad'))
    def test_no_unreachable_hidden_submenus(self):
        with self.assertRaises(AssertionError):validate(ui=UI.replace('<summary>Ordina pagine</summary>', '<div>Ordina pagine</div>'))
    def test_no_regressed_default_fonts(self):
        with self.assertRaises(AssertionError):validate(typo=TYPO.replace("{fontFamily:'Arial'}",'{}'))
    def test_enforce_keyboard_focus(self):
        with self.assertRaises(AssertionError):validate(css=CSS.replace('.page-editor-thumb-menu-floating .page-editor-thumb-submenu>summary:focus-visible', '.removed-focus-selector'))
    def test_early_preflight_before_npm(self):
        validate()
        self.assertLess(WORKFLOW.index('tools.tests.test_rc224_thumbnail_arials'),WORKFLOW.index('Install reproducibly'))

if __name__=='__main__':unittest.main()
