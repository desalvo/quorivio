"""Fail-closed pre-npm checks for RC223 contextual formatting and surface parity."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()


def validate(ui=UI,css=CSS):
    required_ui=[
        'const [ribbonDismissed,setRibbonDismissed]=useState(true);',
        'const toggleSelection=(id:string,extend=false)=>{setRibbonDismissed(true);',
        'setSelectedWidgets([w.id]);setRibbonDismissed(true);setContextWidget(null);',
        'aria-label="Formato widget" onClick={()=>{setActive(w.id);',
        'setFormatTab(\'text\');setRibbonDismissed(false);setContextWidget(null)',
        'className="widget-format-tabs" role="tablist"',
        "formatTab==='border'",
        "formatTab==='effects'",
        "formatTab==='content'",
        "formatTab==='links'&&w.kind==='results-button'",
        'aria-label="Colore bordo widget"',
        'aria-label="Pagina collegata ai risultati"',
        'aria-label="Stile bordo widget"',
        'aria-label="Visibilità e contenuti widget"',
        "allowScale={w.autoFit!==false&&!['qr','participant-count'].includes(w.kind)",
        'className="participant-qr-url" href={url} title={url}',
    ]
    required_css=[
        '/* RC223: footer uses the authored paragraph and vertical alignment',
        '[data-vertical-align="middle"] .widget-fit-content{justify-content:center!important}',
        '[data-vertical-align="bottom"] .widget-fit-content{justify-content:flex-end!important}',
        'flex:0 0 auto!important;text-align:inherit!important;',
        '.widget-format-tabs button[aria-selected="true"]',
        'white-space:nowrap!important;word-break:normal!important;',
        'container-type:size;width:100%!important;height:100%!important;',
        '.projection-participant-count [data-live-participants]',
        'max-height:min(390px,calc(100dvh - 16px))!important;',
    ]
    for needle in required_ui:
        if needle not in ui:raise AssertionError('missing widget interaction contract: '+needle)
    for needle in required_css:
        if needle not in css:raise AssertionError('missing layout contract: '+needle)


class RC223FormatLayout(unittest.TestCase):
    def test_context_only_format_and_all_tabs(self):validate()
    def test_negative_auto_open_selection(self):
        with self.assertRaisesRegex(AssertionError,'interaction contract'):
            validate(ui=UI.replace('const toggleSelection=(id:string,extend=false)=>{setRibbonDismissed(true);','const toggleSelection=(id:string,extend=false)=>{setRibbonDismissed(false);',1))
    def test_negative_font_overlay_reappears_on_doubleclick(self):
        with self.assertRaisesRegex(AssertionError,'interaction contract'):
            validate(ui=UI.replace('setSelectedWidgets([w.id]);setRibbonDismissed(true);setContextWidget(null);','setSelectedWidgets([w.id]);setRibbonDismissed(false);setContextWidget(null);',1))
    def test_negative_editor_footer_forced_center(self):
        with self.assertRaisesRegex(AssertionError,'layout contract'):
            validate(css=CSS.replace('flex:0 0 auto!important;text-align:inherit!important;','flex:0 0 auto!important;text-align:center!important;',1))
    def test_negative_qr_url_multiline(self):
        with self.assertRaisesRegex(AssertionError,'layout contract'):
            validate(css=CSS.replace('white-space:nowrap!important;word-break:normal!important;','white-space:normal!important;word-break:break-word!important;',1))
    def test_negative_qr_whole_widget_scaling(self):
        with self.assertRaisesRegex(AssertionError,'interaction contract'):
            validate(ui=UI.replace("allowScale={w.autoFit!==false&&!['qr','participant-count'].includes(w.kind)","allowScale={"))
    def test_ci_must_run_before_npm_and_browser(self):
        self.assertIn('tools.tests.test_rc223_format_layout',CI)
        self.assertIn('tools/ci_rc223_widget_layout_chromium.py',CI)
        self.assertLess(CI.index('tools.tests.test_rc223_format_layout'),CI.index('Install reproducibly'))

if __name__=='__main__':unittest.main()
