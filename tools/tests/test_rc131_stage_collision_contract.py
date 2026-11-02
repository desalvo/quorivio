"""Fail early if continuous drag and authored audience typography are weakened."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
PLACEMENT=(ROOT/'apps/web/src/widget-placement.ts').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
APP=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC131StageAndCollision(unittest.TestCase):
 def test_analytic_continuous_first_contact_and_fail_closed(self):
  self.assertIn('function sweptContact(a:Box,b:Box,dx:number,dy:number)',PLACEMENT)
  self.assertIn('const enter=Math.max(x[0],y[0]),leave=Math.min(x[1],y[1])',PLACEMENT)
  self.assertIn('firstContact=Math.min(firstContact,contact)',PLACEMENT)
  self.assertIn('return overlapsOtherWidgets(stopped,ids)?original:stopped',PLACEMENT)
  self.assertIn('const target=moveWidgetGroup(original,ids,dx,dy)',PLACEMENT)
  self.assertNotIn('const segments=Math.min(400',PLACEMENT)
 def test_audience_fidelity_respects_explicit_font_at_all_widths(self):
  self.assertIn("'--authored-widget-font-size':widgetTypographyStyle(w.style).fontSize",APP)
  self.assertIn('.audience-widget-layout.stage-fidelity>.page-widget{font-size:var(--authored-widget-font-size,1.25cqw)!important;}',CSS)
  self.assertIn('stage-reading>.page-widget',CSS)
  self.assertIn('font-size:1rem!important',CSS)
 def test_real_chromium_and_node_regressions_are_required(self):
  self.assertIn('tools/ci_rc131_stage_fidelity_chromium.py',WORKFLOW)
  self.assertIn('apps/web/test/rc131-continuous-collision.test.ts',WORKFLOW)
  self.assertIn('tools.tests.test_rc131_stage_collision_contract',WORKFLOW)
  self.assertIn('tools/verify_rc_cycle131_inventory.py',WORKFLOW)

if __name__=='__main__':unittest.main()
