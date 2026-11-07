"""Fail-closed pre-npm contract against the RC249 false-negative zoom fixture."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def valid(ui,layout,chromium,workflow):
    return (ui.count('Number.parseFloat(getComputedStyle(document.documentElement).zoom)||1')==2
      and 'event.anchor,rootZoom' in ui and 'bottom:rect.bottom},rootZoom' in ui
      and 'const zoomObserver=new MutationObserver(reposition)' in ui
      and 'zoomObserver.disconnect()' in ui
      and 'rootZoom=1' in layout and 'left:left/factor' in layout
      and 'maxHeight:maxHeight/factor' in layout
      and 'getComputedStyle(document.documentElement).zoom' in chromium
      and 'await trigger.click(timeout=2500)' in chromium
      and "group.get_by_text('Esporta e dati').click()" in chromium
      and 'python3 tools/ci_rc250_thumbnail_zoom_chromium.py' in workflow
      and 'python3 tools/ci_browser_editor.py' in workflow)

class ThumbnailMenuZoomRC250(unittest.TestCase):
    def test_real_zoom_is_applied_in_both_placement_paths(self):
        ui=(ROOT/'apps/web/src/main.tsx').read_text()
        layout=(ROOT/'apps/web/src/thumbnail-menu-layout.ts').read_text()
        chromium=(ROOT/'tools/ci_rc250_thumbnail_zoom_chromium.py').read_text()
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertTrue(valid(ui,layout,chromium,workflow))
        self.assertFalse(valid(ui.replace('event.anchor,rootZoom','event.anchor'),layout,chromium,workflow))
        self.assertFalse(valid(ui.replace('bottom:rect.bottom},rootZoom','bottom:rect.bottom}'),layout,chromium,workflow))
        self.assertFalse(valid(ui,layout.replace('left:left/factor','left'),chromium,workflow))
        self.assertFalse(valid(ui,layout,chromium.replace("await trigger.click(timeout=2500)","await trigger.click(force=True)"),workflow))
    def test_existing_compiled_react_acceptance_still_mandatory(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertLess(workflow.index('RC250 browser root zoom menu before npm'),workflow.index('actions/setup-node@'))
        self.assertIn('python3 tools/ci_rc249_thumbnail_trigger_chromium.py',workflow)
        self.assertIn('python3 tools/ci_browser_editor.py',workflow)

if __name__=='__main__':unittest.main()
