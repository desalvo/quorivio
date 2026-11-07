"""RC251: fail-closed public native zoom contract, with negative mutations."""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parents[2]

def contract(zoom:str,ui:str,ci:str,browser:str,css:str)->bool:
    return all(token in zoom for token in (
        "export function isUnscaledPublicSurface(pathname:unknown):boolean{",
        "pathname.startsWith('/join/')",
        "pathname.startsWith('/screen/')",
        "if(isUnscaledPublicSurface(pathname))return '100%'",
        'GLOBAL_ZOOM_BASE=0.8',
    )) and all(token in ui for token in (
        "zoomStyleValue(zoom,window.location.pathname)",
        'const isLiveSurface=isUnscaledPublicSurface(window.location.pathname)',
        '{!isLiveSurface&&<aside className="global-page-zoom"',
        "root.style.setProperty('zoom',value)",
        "root.style.setProperty(GLOBAL_ZOOM_CSS_VARIABLE,String(Number.parseFloat(value)/100))",
    )) and all(token in ci for token in (
        'RC251 public-native zoom and phone touch accessibility before npm',
        'tools.tests.test_rc251_public_live_zoom_ci',
        'apps/web/test/rc251-public-live-zoom.test.ts',
        'python3 tools/ci_rc251_public_zoom_chromium.py',
        'python3 tools/ci_browser_participant.py',
        'python3 tools/verify_rc_cycle250_inventory.py --historical',
        'python3 tools/verify_rc_cycle251_inventory.py',
    )) and all(token in browser for token in (
        "('previous_root_zoom','80%')",
        "('rc251_public_live','100%')",
        "row['height']>=43.5",
        "abs(fixed['width']-390)<2",
    )) and '.audience-widget-layout.stage-phone' in css

class PublicLiveZoomCI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zoom=(ROOT/'apps/web/src/global-page-zoom.ts').read_text()
        cls.ui=(ROOT/'apps/web/src/main.tsx').read_text()
        cls.ci=(ROOT/'.github/workflows/ci.yml').read_text()
        cls.browser=(ROOT/'tools/ci_rc251_public_zoom_chromium.py').read_text()
        cls.css=(ROOT/'apps/web/src/style.css').read_text()
    def valid(self,**changes):
        data={'zoom':self.zoom,'ui':self.ui,'ci':self.ci,'browser':self.browser,'css':self.css}
        return contract(**(data|changes))
    def test_source_and_pipeline_are_separated(self):
        self.assertTrue(self.valid())
        self.assertLess(self.ci.index('RC251 public-native zoom and phone touch accessibility before npm'),self.ci.index('actions/setup-node@'))
        self.assertLess(self.ci.index('python3 tools/ci_rc251_public_zoom_chromium.py'),self.ci.index('python3 tools/ci_browser_participant.py'))
        ast.parse(self.browser)
    def test_negative_unscaled_route_removed(self):
        self.assertFalse(self.valid(zoom=self.zoom.replace("if(isUnscaledPublicSurface(pathname))return '100%'",'// missing')))
        self.assertFalse(self.valid(zoom=self.zoom.replace("pathname.startsWith('/join/')",'false')))
        self.assertFalse(self.valid(zoom=self.zoom.replace("pathname.startsWith('/screen/')",'false')))
    def test_negative_live_surface_control_leaked(self):
        self.assertFalse(self.valid(ui=self.ui.replace('{!isLiveSurface&&<aside className="global-page-zoom"','{<aside className="global-page-zoom"')))
        self.assertFalse(self.valid(ui=self.ui.replace('zoomStyleValue(zoom,window.location.pathname)','zoomStyleValue(zoom)')))
    def test_negative_skip_real_browser_and_historical_integrity(self):
        self.assertFalse(self.valid(ci=self.ci.replace('python3 tools/ci_browser_participant.py','echo skipped')))
        self.assertFalse(self.valid(ci=self.ci.replace('python3 tools/verify_rc_cycle250_inventory.py --historical','echo skipped')))
        self.assertFalse(self.valid(browser=self.browser.replace("row['height']>=43.5",'True')))

if __name__=='__main__':unittest.main()
