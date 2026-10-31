"""RC84: historical editor menu contract follows current native capture routing."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class Cycle84HistoricalContextCompat(unittest.TestCase):
 def test_old_test_checks_actual_native_capture_and_portal(self):
  old=(ROOT/'tools/tests/test_rc_cycle37_editor_ux.py').read_text()
  for requirement in ('onContextMenuCapture={handleCanvasContext}',
    'openWidgetContextMenu(widgetId,widget,e.clientX,e.clientY)',
    'clearContextHold();clearWidgetHold();positionMenu(element,x,y)',
    'positionMenu(widgetElement)',
    'positionMenu(e.currentTarget);setContextWidget(w.id)',
    'contextWidget===w.id&&createPortal('):
   self.assertIn(requirement,old)
  self.assertNotIn("self.assertIn('positionMenu(e.currentTarget,e.clientX,e.clientY)',UI)",old)
 def test_legacy_contract_is_early_and_still_runs_in_full_suite(self):
  wf=(ROOT/'.github/workflows/ci.yml').read_text()
  cmd='tools.tests.test_rc_cycle37_editor_ux'
  self.assertIn(cmd,wf)
  self.assertLess(wf.index(cmd),wf.index('npm install --ignore-scripts'))
  self.assertIn('python3 -m unittest discover -s tools/tests -v',wf)
 def test_real_widget_menu_is_not_replaced_by_page_background_menu(self):
  ui=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn('if(widgetId&&widgets.some(w=>w.id===widgetId))',ui)
  self.assertIn('openWidgetContextMenu(widgetId,widget,e.clientX,e.clientY)',ui)
  self.assertIn('clearContextHold();openBlankMenu()',ui)
  self.assertIn('e.preventDefault();e.stopPropagation()',ui)
