"""Fail early if continuous drag and authored audience typography are weakened."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
PLACEMENT=(ROOT/'apps/web/src/widget-placement.ts').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
APP=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC131StageAndCollision(unittest.TestCase):
 def test_free_overlap_with_canvas_boundary_and_nonmutating_pointers(self):
  self.assertIn('export function moveWidgetsToCollisionLimit',PLACEMENT)
  self.assertIn('return moveWidgetGroup(original,ids,dx,dy)',PLACEMENT)
  self.assertIn('proposed.x+proposed.width>100.0001',PLACEMENT)
  self.assertIn('return proposed;',PLACEMENT)
  self.assertNotIn('const segments=Math.min(400',PLACEMENT)
 def test_audience_fidelity_respects_explicit_font_at_all_widths(self):
  # RC159: title typography resolves the page/master style first; all other
  # widgets continue using their own saved style. The legacy literal check
  # silently assumed every kind had the same source fields.
  self.assertIn("'--authored-widget-font-size':widgetTypographyStyle(w.kind==='title'?widgetDisplay(w,{pageTitle:entry.activity.title,masterTitleStyle:entry.theme?.master?.titleStyle}).style:w.style).fontSize",APP)
  self.assertIn("...widgetTypographyStyle(w.kind==='title'?widgetDisplay(w,{pageTitle:entry.activity.title,masterTitleStyle:entry.theme?.master?.titleStyle}).style:w.style)",APP)
  self.assertIn('.audience-widget-layout.stage-fidelity>.page-widget{font-size:var(--authored-widget-font-size,1.25cqw)!important;}',CSS)
  self.assertIn('stage-reading>.page-widget',CSS)
  self.assertIn('font-size:1rem!important',CSS)
 def test_real_chromium_and_node_regressions_are_required(self):
  self.assertIn('tools/ci_rc131_stage_fidelity_chromium.py',WORKFLOW)
  self.assertIn('apps/web/test/rc131-continuous-collision.test.ts',WORKFLOW)
  self.assertIn('tools.tests.test_rc131_stage_collision_contract',WORKFLOW)
  self.assertIn('tools/verify_rc_cycle131_inventory.py',WORKFLOW)

if __name__=='__main__':unittest.main()
