"""RC132 early source contracts: pointer/keyboard geometry parity and accessible response field."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
APP=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
SELECTION=(ROOT/'apps/web/src/widget-selection.ts').read_text(encoding='utf8')
GEOMETRY=(ROOT/'apps/web/src/widget-placement.ts').read_text(encoding='utf8')
RESIZE=(ROOT/'apps/web/src/answer-field-resize.ts').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC132KeyboardAndAnswerBox(unittest.TestCase):
 def test_keyboard_pointer_share_slide_boundaries_without_collision_rejection(self):
  self.assertIn('else if(!e.altKey&&!e.shiftKey)onChange(moveWidgetsToCollisionLimit(widgets,[w.id]',APP)
  self.assertIn('return moveWidgetsToCollisionLimit(widgets,existingWidgetIds(widgets,ids),dx,dy)',SELECTION)
  self.assertIn('return moveWidgetGroup(original,ids,dx,dy)',GEOMETRY)
 def test_resize_handle_is_keyboard_focused_and_bounded(self):
  self.assertIn('role="slider" tabIndex={0}',APP)
  self.assertIn("{w.kind==='topic-question'&&<div className=\"canvas-widget-answer-preview\"><EditorAnswerFieldPreview questionField",APP)
  self.assertIn('questionField?"Casella domanda libera nell’editor"',APP)
  for marker in ('aria-valuemin={48}','aria-valuemax={400}','aria-valuenow={height}', 'aria-valuetext={`${height} pixel logici`}',
                 'onKeyDown={e=>{if(e.altKey||e.ctrlKey||e.metaKey)return;',
                 'e.preventDefault();e.stopPropagation();if(next===height)return;',
                 'onBeginGesture?.();onHeightChange(next);onEndGesture?.()'):
   self.assertIn(marker,APP)
  self.assertIn("[role=slider]'))return;",APP)
  self.assertIn('.widget-answer-height-handle:focus-visible',CSS)
  for key in ('ArrowDown','ArrowUp','PageDown','PageUp','Home','End'):
   self.assertIn("case '"+key+"':",RESIZE)
  self.assertIn('MAX_ANSWER_FIELD_HEIGHT = 400',RESIZE)
  self.assertIn('MIN_ANSWER_FIELD_HEIGHT = 48',RESIZE)
 def test_new_behavior_runs_in_early_and_late_ci(self):
  self.assertIn('tools.tests.test_rc132_keyboard_accessibility',WORKFLOW)
  self.assertIn('apps/web/test/rc132-keyboard-geometry.test.ts',WORKFLOW)
  self.assertIn('tools/verify_rc_cycle132_inventory.py',WORKFLOW)
  self.assertIn('tools/ci_rc131_stage_fidelity_chromium.py',WORKFLOW)

if __name__=='__main__':unittest.main()
