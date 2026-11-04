"""RC172: editable phone overrides never corrupt automatic phone placements."""
from __future__ import annotations
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LAYOUT=(ROOT/'apps/web/src/mobile-page-layout.ts').read_text(encoding='utf8')
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
POLICY=(ROOT/'apps/web/src/live-slide-policy.ts').read_text(encoding='utf8')

class RC172PhoneMixedAuthoring(unittest.TestCase):
 def test_manual_positions_reserve_slots_before_automatic_placement(self):
  self.assertIn('const reservations=fixed.map(',LAYOUT)
  self.assertIn('const clash=reservations.find(',LAYOUT)
  self.assertIn('candidate=clash.end+MOBILE_GAP',LAYOUT)
  self.assertIn('mobile?.positions?.[w.id]??layout.defaults.get(w.id)',LAYOUT)

 def test_editor_and_public_use_same_authored_mobile_stage_height(self):
  self.assertIn('mobileStageHeight(pageWidgets,mobileLayoutDraft)',UI)
  self.assertIn('mobileStageHeight(visible, mobile)',POLICY)
  self.assertIn('mobilePageWidgets(visible, mobile)',POLICY)

 def test_compacting_positions_cannot_delete_phone_typography(self):
  self.assertIn('setMobileLayoutDraft(old=>({...old,positions:undefined}))',UI)
  self.assertNotIn('positions:undefined,styles:undefined',UI)

 def test_negative_missing_reservation_would_fail(self):
  broken=LAYOUT.replace('candidate=clash.end+MOBILE_GAP','candidate+=MOBILE_GAP',1)
  self.assertNotIn('candidate=clash.end+MOBILE_GAP',broken)
  self.assertIn('candidate=clash.end+MOBILE_GAP',LAYOUT)

if __name__=='__main__': unittest.main()
