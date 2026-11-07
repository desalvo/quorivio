"""RC249 fail-closed guard: a body-portal menu cannot cover its own trigger."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def valid(ui,layout,css,workflow):
    return all(x in ui for x in (
        'event.anchor',
        'anchor:{left:box.left,right:box.right,top:box.top,bottom:box.bottom}',
        'window.addEventListener(\'scroll\',reposition,true)',
        'window.addEventListener(\'resize\',reposition)',
        "window.visualViewport?.addEventListener('resize',reposition)",
        "'--thumbnail-menu-width':`${pageMenuPosition.width}px`",
        'setPageMenuPosition(old=>old.left===next.left',
    )) and all(x in layout for x in (
        'export type ThumbnailMenuAnchor=',
        'const freeRight=',
        'const freeLeft=',
        'anchor.right+gap',
        'anchor.left-gap-width',
        'const below=',
        'const above=',
    )) and 'width:var(--thumbnail-menu-width,' in css and all(x in workflow for x in (
        'tools.tests.test_rc249_thumbnail_trigger_contract',
        'apps/web/test/rc249-thumbnail-menu-anchor.test.ts',
        'python3 tools/ci_rc249_thumbnail_trigger_chromium.py',
        'python3 tools/ci_browser_editor.py',
    ))

class ThumbnailMenuRC249(unittest.TestCase):
    def test_actual_source_safeguards(self):
        ui=(ROOT/'apps/web/src/main.tsx').read_text()
        layout=(ROOT/'apps/web/src/thumbnail-menu-layout.ts').read_text()
        css=(ROOT/'apps/web/src/style.css').read_text()
        ci=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertTrue(valid(ui,layout,css,ci))
        self.assertFalse(valid(ui.replace("window.addEventListener('scroll',reposition,true)",''),layout,css,ci))
        self.assertFalse(valid(ui.replace('event.anchor','undefined'),layout,css,ci))
        self.assertFalse(valid(ui,layout.replace('anchor.left-gap-width','anchor.left'),css,ci))
        self.assertFalse(valid(ui,layout,css.replace('width:var(--thumbnail-menu-width,','width:min('),ci))
    def test_workflow_has_pre_npm_gate_and_real_chromium_regression(self):
        ci=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertLess(ci.index('RC249 anchored thumbnail menu before npm'),ci.index('actions/setup-node@'))
        self.assertIn('python3 tools/ci_editor_mock_layout_chromium.py',ci)
        self.assertIn('python3 tools/ci_rc224_thumbnail_menu_chromium.py',ci)

if __name__=='__main__':unittest.main()
