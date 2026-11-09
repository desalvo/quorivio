"""RC85: avoid reflow between native secondary-button down and contextmenu."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class RC85SecondaryPointerContext(unittest.TestCase):
 def test_react_selection_guard_is_first_in_widget_pointer_handler(self):
  main=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn("import {startsWidgetSelectionOnPointerDown} from './editor-context-input'",main)
  self.assertIn("onPointerDown={e=>{if(!startsWidgetSelectionOnPointerDown(e.button))return;if(e.shiftKey)",main)
  self.assertIn('onContextMenuCapture={handleCanvasContext}',main)
  self.assertIn('onPointerDownCapture={e=>{',main)
  self.assertIn('const pointer=contextPointer.current;',main)
  self.assertIn('Math.hypot(pointer.x-e.clientX,pointer.y-e.clientY)<8',main)
  self.assertIn('openWidgetContextMenu(widgetId,widget,e.clientX,e.clientY)',main)
 def test_secondary_button_is_never_allowed_to_reflow_the_canvas(self):
  module=(ROOT/'apps/web/src/editor-context-input.ts').read_text()
  self.assertIn('return button===0;',module)
  tests=(ROOT/'apps/web/test/editor-context-input.test.ts').read_text()
  for word in ('(0),true','(1),false','(2),false','(-1),false'):
   self.assertIn(word,tests)
 def test_existing_context_menu_and_live_chromium_contract_remain_mandatory(self):
  wf=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('tools.tests.test_rc_cycle85_secondary_pointer_context',wf)
  self.assertLess(wf.index('tools.tests.test_rc_cycle85_secondary_pointer_context'),wf.index('npm ci --ignore-scripts'))
  self.assertIn('python3 tools/ci_browser_editor.py',wf)
