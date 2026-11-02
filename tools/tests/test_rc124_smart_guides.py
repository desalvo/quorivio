"""Fail-closed source integration contract for PowerPoint-like smart guides."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
PLACE=(ROOT/'apps/web/src/widget-placement.ts').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC124SmartGuides(unittest.TestCase):
 def test_guides_are_transient_and_editor_only(self):
  self.assertIn('setAlignmentGuides([]);',MAIN)
  self.assertIn('alignmentGuides.length>0&&<div className="widget-alignment-guides" aria-hidden="true"',MAIN)
  # The RC128 sweep permits partial travel to the first obstacle; guides
  # appear only when the proposed magnetic snap is actually reachable.
  self.assertIn('setAlignmentGuides(accepted.find(w=>w.id===g.id)',MAIN)
  self.assertIn('?guides:[])',MAIN)
  self.assertIn('pointer-events:none',CSS)
  self.assertIn('.slide-scheme-workspace .widget-canvas > .widget-alignment-guides',CSS)
  self.assertIn('magneticSnapWithGuides',PLACE)
  self.assertIn('export function magneticSnapWidget',PLACE) # legacy call compatibility
 def test_grid_snaps_final_coordinates_and_disables_other_magnets(self):
  self.assertIn('snapGrid?snapWidgetGroupDelta(base,ids,dx,dy)',MAIN)
  self.assertIn('if(!snapGrid&&ids.length===1)',MAIN)
  self.assertIn('Math.round((left+dx)/step)*step-left',PLACE)
  self.assertIn('Math.round((top+dy)/step)*step-top',PLACE)
  self.assertIn('background-size:5% 5%',CSS)
 def test_bounded_collision_and_pointer_safety_not_bypassed(self):
  self.assertIn('moveWidgetsToCollisionLimit(base,ids,candidate.x-origin.x,candidate.y-origin.y)',MAIN)
  self.assertIn('onChange(accepted);return;',MAIN)
  # Geometry must stop at the first obstacle even when the pointer leaps
  # beyond a narrow widget. Do not weaken these guards to make CI green.
  self.assertIn('overlapsOtherWidgets(moveWidgetGroup(original,ids,dx*t,dy*t),ids)',PLACE)
  self.assertIn('return moveWidgetGroup(original,ids,dx*low,dy*low)',PLACE)
  self.assertIn('return moveWidgetGroup(original,ids,dx*lo,dy*lo)',PLACE)
  self.assertIn('apps/web/test/rc128-preview-recovery-collision.test.ts',WORKFLOW)
  self.assertIn('onEndGesture?.()',MAIN)
  self.assertIn('widget-alignment-guide.axis-x',CSS)
  self.assertIn('widget-alignment-guide.axis-y',CSS)
 def test_ci_verifies_node_and_real_browser(self):
  self.assertIn('apps/web/test/rc124-smart-guides.test.ts',WORKFLOW)
  self.assertIn('tools/ci_rc124_alignment_guides_chromium.py',WORKFLOW)
  self.assertIn('tools.tests.test_rc124_smart_guides',WORKFLOW)

if __name__=='__main__':unittest.main()
