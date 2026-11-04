"""RC175 media geometry preflight, including negative mutation regressions."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def valid(css: str, ui: str) -> bool:
    public=ui[ui.find('{joinPath?<main id="main-content"'):ui.find('publicPath?<PresenterLiveScreen')]
    return all((
        'w.kind===\'video\'&&w.assetId?<video className="projection-media"' in public,
        'className="projection-media" src={`/api/join/' in public,
        '>.page-widget .widget-fit-content > :is(img.projection-media,video.projection-media){' in css,
        'width:100%!important;height:100%!important;max-height:100%!important;' in css,
        '>.widget-fit-frame>.widget-fit-content{height:100%!important;min-height:0!important;}' in css,
        '.audience-widget-layout.stage-reading{\n  background:#fff!important;background-image:none!important;' in css,
    ))

class RC175Media(unittest.TestCase):
    def test_contract(self):self.assertTrue(valid(CSS,UI))
    def test_negative_height_rule(self):self.assertFalse(valid(CSS.replace('>.widget-fit-frame>.widget-fit-content{height:100%!important','>.widget-fit-frame>.widget-fit-content{height:auto!important'),UI))
    def test_negative_media_rule(self):self.assertFalse(valid(CSS.replace('>.page-widget .widget-fit-content > :is(img.projection-media,video.projection-media){','>.page-widget .widget-fit-content > :is(img.projection-media){'),UI))
    def test_negative_video_class(self):self.assertFalse(valid(CSS,UI.replace('w.kind===\'video\'&&w.assetId?<video className="projection-media"','w.kind===\'video\'&&w.assetId?<video',1)))
    def test_browser_probe_is_after_dependency_step(self):
        self.assertIn('python3 tools/rc175_browser_media_geometry.py',CI)
        self.assertLess(CI.index("'playwright>=1.50,<2'"),CI.index('python3 tools/rc175_browser_media_geometry.py'))

if __name__=='__main__':unittest.main()
