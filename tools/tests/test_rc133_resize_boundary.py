"""RC133 early safety: eight-edge and keyboard resizes must stop, not bounce."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
PLACEMENT=(ROOT/'apps/web/src/widget-placement.ts').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC133ResizeBoundary(unittest.TestCase):
 def test_pointer_resizes_from_original_gesture_not_intermediate_widget(self):
  self.assertIn('const base=g.groupBase||widgets;',MAIN)
  self.assertIn('const resized=resizeWidgetToCollisionLimit(base,g.id,nextPos);',MAIN)
  self.assertIn("const corner=['nw','ne','sw','se'].includes(g.edge)",MAIN)
  self.assertIn('onChange(resized.map(w=>w.id===g.id?{...w,qrImagePixels:pixels}:w));',MAIN)
  self.assertIn('}else onChange(resized);',MAIN)
  self.assertIn('onBeginGesture?.();',MAIN)
  self.assertIn('onEndGesture?.()',MAIN)
 def test_keyboard_resize_same_collision_limit_but_rotation_preserved(self):
  self.assertIn('else if(e.shiftKey&&!e.altKey)onChange(resizeWidgetToCollisionLimit(widgets,w.id,position));',MAIN)
  self.assertIn('else onChange(rejectWidgetCollisions(widgets',MAIN)
  self.assertIn("g.edge.includes('w')",MAIN)
  self.assertIn("g.edge.includes('n')",MAIN)
 def test_collision_math_fail_closed_no_forced_click_or_unsafe_skipping(self):
  self.assertIn('export function resizeWidgetToCollisionLimit',PLACEMENT)
  self.assertIn('proposed.x+proposed.width>100.0001',PLACEMENT)
  self.assertIn('proposed.y+proposed.height>100.0001',PLACEMENT)
  self.assertNotIn('autoFit:false',PLACEMENT)
  self.assertNotIn('force: true',MAIN)
 def test_cancelled_response_resize_reverts_to_pointer_down_height(self):
  self.assertIn('const cancel=(e:React.PointerEvent<HTMLSpanElement>)=>{const start=drag.current;',MAIN)
  self.assertIn('drag.current=null;onHeightChange(start.height);onEndGesture?.()',MAIN)
  self.assertIn('onPointerUp={stop} onPointerCancel={cancel} onLostPointerCapture={stop}',MAIN)
 def test_verified_at_early_late_ci_and_preserves_release_guards(self):
  self.assertIn('tools.tests.test_rc133_resize_boundary',WORKFLOW)
  self.assertIn('apps/web/test/rc133-resize-limit.test.ts',WORKFLOW)
  self.assertIn('tools/verify_rc_cycle133_inventory.py',WORKFLOW)
  self.assertIn('tools/verify_rc_cycle132_inventory.py --historical',WORKFLOW)
  self.assertIn('needs.rc-campaign-conclusion.result',WORKFLOW)
  self.assertIn('!inputs.rc_acceptance_suite',WORKFLOW)

if __name__=='__main__':unittest.main()
