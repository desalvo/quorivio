"""RC145 contracts: smartphone backdrop isolation and editor/preview typefaces."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding='utf8')


class MobileBackgroundFontParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui = read('apps/web/src/main.tsx')
        cls.css = read('apps/web/src/style.css')

    def test_background_upload_sets_only_phone_when_phone_selected(self):
        method = self.ui.split('async function uploadBackground(', 1)[1].split('async function deleteAsset(', 1)[0]
        self.assertIn('if(forMobile){setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));}', method)
        self.assertIn('else if(forResults){setResultBackgroundAsset(applied.id)', method)
        self.assertIn('else{setQuestionBackgroundAsset(applied.id)', method)
        self.assertIn("onBackgroundUpload={file=>uploadBackground(file,false,canvasDevice==='phone')}", self.ui)

    def test_library_select_background_only_routes_phone_image_to_mobile_layout(self):
        method = self.ui.split('function selectLibraryBackground(', 1)[1].split('async function uploadBackground(', 1)[0]
        self.assertEqual(method.count('if(forMobile)'), 1)
        self.assertIn('if(forMobile)setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));', method)
        self.assertIn('selectLibraryBackground(id,false,true)', self.ui)

    def test_solid_mobile_background_replaces_mobile_image_not_desktop(self):
        self.assertIn('onBackgroundColorChange={color=>setMobileLayoutDraft(old=>({...old,backgroundColor:color,backgroundAssetId:undefined}))}', self.ui)
        self.assertIn('mobileMode&&<label>Colore di sfondo smartphone', self.ui)
        self.assertIn('mobileLayoutDraft.backgroundAssetId||\'\':slideBackground({backgroundAssetId:questionBackgroundAsset||undefined,backgroundUrl:questionBackground||undefined},snap.session.theme).assetId||\'\'', self.ui)
        self.assertIn('background-image:var(--editor-page-background,none)!important;', self.css)
        self.assertIn("backgroundImage:viewActivity?.page_design?.mobile?.backgroundAssetId?", self.ui)

    def test_editor_projection_arial_heading_and_rich_text_parity(self):
        typography = read('apps/web/src/widget-appearance.ts')
        self.assertIn("fontFamily:style?.fontFamily||'Arial'", typography)
        self.assertIn('font-family:inherit!important;font-weight:inherit!important;', self.css)
        self.assertIn(' :is(h1,h2,h3,h4){font-family:inherit;}', self.css)
        self.assertIn("...widgetTypographyStyle(w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).style:widgetTextDefaults(w.kind,w.style))", self.ui)

    def test_release_gate_remains_unchanged(self):
        self.assertIn('85.25%', read('docs/RC_CYCLE145_MOBILE_BACKGROUND_FONT_PARITY.en.md'))
        for flag in ('rc_strict=false', 'publish_image=false', 'publish_latest=false'):
            self.assertIn(flag, read('docs/RC_CYCLE145_MOBILE_BACKGROUND_FONT_PARITY.en.md'))


if __name__ == '__main__':
    unittest.main()
