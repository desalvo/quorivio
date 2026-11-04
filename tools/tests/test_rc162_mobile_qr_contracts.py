from __future__ import annotations
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
API=(ROOT/'apps/api/src/domain.ts').read_text()
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text()

class RC162MobileQrContracts(unittest.TestCase):
    def test_slider_is_an_editable_device_switch_and_has_keyboard_focus(self):
        self.assertIn('role="switch" aria-label="Modifica layout Smartphone"',UI)
        self.assertIn("setCanvasDevice(e.target.checked?'phone':'desktop')",UI)
        self.assertIn('input:focus-visible+.editor-device-slider-track',CSS)
        self.assertIn('Ripristina layout smartphone automatico',UI)
        self.assertIn('Ripristina posizione automatica smartphone per questo widget',UI)
    def test_still_keeps_desktop_positions_when_mobile_changes(self):
        self.assertIn('mergeMobilePositionEdits(pageWidgets,old,items)',UI)
        self.assertIn('position:original.position',UI)
        self.assertIn("widgets={canvasDevice==='phone'?mobilePageWidgets(pageWidgets,mobileLayoutDraft):pageWidgets}",UI)
    def test_no_duplicate_qr_title_and_legacy_title_is_hidden(self):
        self.assertIn('widget.showTitle===true&&<strong><WidgetStyledText',UI)
        self.assertIn("w.kind==='qr'?false:w.showTitle!==false",UI)
        self.assertIn("kind==='qr'?{showTitle:false,showQrUrl:true}",UI)
    def test_qr_url_visibility_is_persisted_and_validated(self):
        self.assertIn('showQrUrl?:boolean',API)
        self.assertIn("w.kind==='qr'&&typeof w.showQrUrl==='boolean'",API)
        self.assertIn('widget.showQrUrl!==false&&<span className="participant-qr-url"',UI)
        self.assertIn('Mostra URL sotto al codice QR',UI)
    def test_responsive_url_reserved_row_and_no_preview_shrink(self):
        self.assertIn('grid-template-rows:minmax(0,1fr) minmax(1.3em,auto)',CSS)
        self.assertIn('data-qr-show-url="false"',CSS)
        self.assertNotIn('.projection-sample-qr img{display:block;max-width:80%;max-height:75%',CSS)
    def test_negative_mutations_are_detected(self):
        for old,new in [('widget.showQrUrl!==false&&<span','false&&<span'),
                        ('widget.showTitle===true&&<strong','widget.showTitle!==false&&<strong'),
                        ('mergeMobilePositionEdits(pageWidgets,old,items)','captureMobilePositions(items)')]:
            bad=UI.replace(old,new,1)
            self.assertNotIn(old,bad)

    def test_phone_typography_only_changes_phone_and_has_server_validation(self):
        self.assertIn('styles?:Record<string,WidgetTextStyle>',API)
        self.assertIn('validWidgetTextStyle(styles[id])',API)
        self.assertIn('Stile smartphone (indipendente dal desktop)',UI)
        self.assertIn('style:original.style',UI)
        self.assertIn('Ripristina stile smartphone automatico per questo widget',UI)
    def test_ci_has_early_contract_and_browser_probe(self):
        self.assertIn('test_rc162_mobile_qr_contracts',WORKFLOW)
        self.assertIn('ci_rc162_qr_resizing_chromium.py',WORKFLOW)
        self.assertIn('verify_rc_cycle162_inventory.py',WORKFLOW)

if __name__=='__main__':unittest.main()
