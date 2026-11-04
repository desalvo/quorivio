"""RC159 real URLs must retain the preview's authored 16:9 slide and title."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()


def parity(ui,css):
    start=ui.find('{joinPath?<main id="main-content"')
    end=ui.find('publicPath?<PresenterLiveScreen',start)
    if start<0 or end<start:return False
    view=ui[start:end]
    return all((
        'const [participantReadingMode,setParticipantReadingMode]=useState(false)' in ui,
        "participantReadingMode?' stage-reading':' stage-fidelity'" in view,
        'participant-slide-title' not in view,
        "['title','footer','text','postit','divider','shape','line'].includes(w.kind)?<ProjectionWidgetContent" in view,
        "masterTitleStyle={entry.theme?.master?.titleStyle}" in view,
        "data-vertical-align={w.style?.verticalAlign||'top'}" in view,
        'stageWidgetTypography(w,{pageTitle:entry.activity.title,masterTitleStyle:entry.theme?.master?.titleStyle},audiencePortrait)' in view,
        'main.participant-live-view{width:min(1280px,96vw)!important' in css,
        'main.participant-live-view .audience-widget-layout.stage-fidelity{min-width:0!important;width:100%!important}' in css,
        '.projection-page-content .projection-widget .projection-slide-title,' in css,
        'font:inherit!important;line-height:inherit!important;margin:0!important;' in css,
    ))

class LivePreviewParity(unittest.TestCase):
    def test_16x9_and_title_contract(self):self.assertTrue(parity(UI,CSS))
    def test_negative_mobile_reading_default(self):self.assertFalse(parity(UI.replace('const [participantReadingMode,setParticipantReadingMode]=useState(false)',"const [participantReadingMode,setParticipantReadingMode]=useState(()=>window.matchMedia('(max-width:700px)').matches)",1),CSS))
    def test_negative_external_title(self):self.assertFalse(parity(UI.replace("{joinStatus==='loading'?", "<div className=\"participant-slide-title\">Broken</div>{joinStatus==='loading'?",1),CSS))
    def test_negative_wrong_title_source(self):self.assertFalse(parity(UI.replace("pageTitle:entry.activity.title,masterTitleStyle:entry.theme?.master?.titleStyle",'pageTitle:entry.session.title,masterTitleStyle:entry.theme?.master?.titleStyle'),CSS))
    def test_negative_no_unified_title_renderer(self):self.assertFalse(parity(UI.replace("['title','footer','text','postit','divider','shape','line'].includes(w.kind)","['footer','text','postit','divider','shape','line'].includes(w.kind)",1),CSS))
    def test_negative_title_sizing(self):self.assertFalse(parity(UI,CSS.replace('font:inherit!important;line-height:inherit!important;margin:0!important;', 'font-size:clamp(35px,4vw,62px);margin:0;',1)))
    def test_ci_preflight_and_browser(self):
        self.assertIn('tools.tests.test_rc159_live_preview_parity',CI)
        self.assertIn('tools/ci_rc159_live_preview_parity_chromium.py',CI)
        self.assertLess(CI.index('tools.tests.test_rc159_live_preview_parity'),CI.index('npm install --ignore-scripts'))
if __name__=='__main__':unittest.main()
