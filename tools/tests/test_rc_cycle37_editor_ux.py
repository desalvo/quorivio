"""Regression contracts for reported screenshot failures in cycle 37."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()

class EditorCycle37(unittest.TestCase):
 def test_default_text_contrast_while_retaining_authored_color(self):
  style=(ROOT/'apps/web/src/widget-appearance.ts').read_text()
  self.assertIn("color:style?.color||'#000000'",style)
  self.assertIn('.editor-ux-v2 .widget-canvas-item{color:#000000;}',CSS)
 def test_widget_menu_escapes_clipping_and_handles_keyboard_touch(self):
  self.assertIn('contextWidget===w.id&&createPortal(',UI)
  self.assertIn('</div>,document.body)}<div className="canvas-layer-tools">',UI)
  self.assertIn('position:fixed!important;z-index:10020',CSS)
  self.assertIn('positionMenu(e.currentTarget,e.clientX,e.clientY)',UI)
  self.assertIn('positionMenu(widgetElement)',UI)
  self.assertIn('positionMenu(e.currentTarget);setContextWidget(w.id)',UI)
 def test_modal_has_safe_fallback_and_close_path(self):
  self.assertIn('class RehearsalErrorBoundary',UI)
  self.assertIn('Chiudi anteprima e torna all\'editor',UI)
  self.assertEqual(UI.count('<RehearsalErrorBoundary '),2)
  self.assertIn('onClick={e=>{if(e.target===e.currentTarget)onClose()}}',UI)
 def test_multichoice_preflight_before_server_patch(self):
  self.assertIn('questionModeOptions(choices,e.target.value)',UI)
  self.assertIn('if(!validPageDesign(question)||!validPageDesign(result))',UI)
  self.assertLess(UI.index('if(!validPageDesign(question)||!validPageDesign(result))'),UI.index('const saved=await request<{ok:boolean;design_revision:number}>'))
