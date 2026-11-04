"""RC171 editor phone toggle, compact layout and graphic palette regression guards."""
from __future__ import annotations
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
LAYOUT=(ROOT/'apps/web/src/mobile-page-layout.ts').read_text(encoding='utf8')

class RC171EditorPhonePalette(unittest.TestCase):
 def test_selector_is_above_palette_not_inside_stage(self):
  header=UI.index('<header className="editor-mock-header">')
  toggle=UI.index('className="editor-device-switch"',header)
  rail=UI.index('className="editor-widget-rail"',header)
  stage=UI.index('className="editor-stage"',header)
  self.assertLess(header,toggle)
  self.assertLess(toggle,rail)
  self.assertLess(toggle,stage)
  self.assertIn('aria-label="Modifica layout Smartphone"',UI)
  self.assertIn('Ricompatta automaticamente',UI)

 def test_graphic_trigger_has_compact_wrapper_and_explicit_menu_button(self):
  self.assertIn('editor-icon-wrapper editor-graphic-wrapper',UI)
  self.assertIn("aria-label={'Scegli tipo e formato: '+label}",UI)
  self.assertIn('onContextMenu={e=>{e.preventDefault();',UI)
  self.assertIn("if(e.pointerType==='mouse')return;clearHold();hold.current",UI)
  self.assertIn('flex-wrap:wrap!important',CSS)
  self.assertIn('.editor-widget-grid .editor-graphic-wrapper{position:relative;flex:0 0 64px!important',CSS)

 def test_negative_unwrapped_legacy_palette_is_rejected(self):
  broken=UI.replace('<span className="editor-icon-wrapper editor-graphic-wrapper">{trigger}', '{trigger}',1)
  self.assertNotIn('editor-icon-wrapper editor-graphic-wrapper',broken)
  self.assertIn('editor-icon-wrapper editor-graphic-wrapper',UI)

 def test_existing_canvas_graphics_have_direct_context_formatting(self):
  self.assertIn('className="canvas-context-graphic-options"',UI)
  self.assertIn('Preset grafico del widget selezionato',UI)
  self.assertIn('Spessore grafico nel menu contestuale',UI)
  self.assertIn('Riempimento forma nel menu contestuale',UI)
  self.assertIn('onContextMenu={e=>{e.preventDefault();e.stopPropagation();openWidgetContextMenu',UI)
  self.assertIn("w.kind!=='line'&&w.kind!=='shape'",UI)

 def test_compact_default_does_not_discard_custom_mobile_positions(self):
  self.assertIn('const MOBILE_GAP=8',LAYOUT)
  self.assertIn('mobile?.positions?.[w.id]??layout.defaults.get(w.id)',LAYOUT)
  self.assertIn('const baseline=Math.max(MOBILE_PAGE_MIN_HEIGHT',LAYOUT)
  self.assertIn("w.kind==='footer'?findFree",LAYOUT)

 def test_negative_old_large_gap_is_rejected(self):
  self.assertNotIn('top+=size+16;',LAYOUT)
  self.assertNotIn('case \'title\':return 90;',LAYOUT)

if __name__=='__main__':unittest.main()
