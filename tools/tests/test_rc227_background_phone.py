"""RC227 no-dependency preflight for modal gallery and adaptive phone layout."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
class RC227BackgroundPhone(unittest.TestCase):
 def test_open_gallery_compact_schema_button(self):
  group=UI.split('<div className="slide-scheme-ribbon"',1)[1].split('<div className="slide-scheme-widget-rail"',1)[0]
  self.assertIn('<SchemaBackgroundTool items=',group)
  self.assertNotIn('<BackgroundGallery items=',group)
  self.assertIn('label="Sfondi"',UI)
 def test_gallery_accessible_modal_esc_focus_and_close(self):
  modal=UI.split('function SchemaBackgroundTool(',1)[1].split('function App(){',1)[0]
  for text in ('role="dialog" aria-modal="true"',"event.key==='Escape'",'previous?.focus()','onSelect={id=>{onSelect(id);setOpen(false)}}','dialogRef.current?.focus()'):
   self.assertIn(text,modal)
 def test_phone_rotation_and_user_selection(self):
  self.assertIn("window.addEventListener('resize',sync)",UI)
  self.assertIn("pointer.addEventListener('change',sync)",UI)
  self.assertIn('if(participantModeExplicit)return;',UI)
  self.assertEqual(UI.count('setParticipantModeExplicit(true)'),3)
 def test_mobile_modal_geometry_rule(self):
  self.assertIn('max-height:calc(100dvh - 24px)',CSS)
  self.assertIn('.schema-background-modal .background-gallery{min-width:0;overflow-y:auto',CSS)
