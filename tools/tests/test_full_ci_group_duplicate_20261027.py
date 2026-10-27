"""Contracts for extended Chromium run 40592859476 group placement failure."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
PLACEMENT=(ROOT/'apps/web/src/widget-selection.ts').read_text()
BROWSER=(ROOT/'tools/ci_browser_editor.py').read_text()

class FullCIGroupDuplicateRegression(unittest.TestCase):
 def test_duplicated_selection_searches_free_group_placement(self):
  self.assertIn('insertWidgetGroupInFreeSpace(widgets,selected,',UI)
  self.assertNotIn('rejectWidgetCollisions(widgets,result.widgets,result.selected)',UI)
 def test_clipboard_group_uses_same_placement_validation(self):
  self.assertIn('insertWidgetGroupInFreeSpace(widgets,copiedWidgets,',UI)
  self.assertIn('overlapsOtherWidgets([...widgets,...translated],newIds)',PLACEMENT)
 def test_no_space_failure_is_reported_not_overlapped(self):
  self.assertIn("if(!result){window.alert('Non c’è spazio per duplicare senza sovrapposizioni.');return}",UI)
  self.assertIn('return null;',PLACEMENT)
 def test_browser_acceptance_detects_rejected_duplicate_alert(self):
  self.assertIn('duplication_alerts',BROWSER)
  self.assertIn("await expect(page.locator('.widget-canvas-item')).to_have_count(5)",BROWSER)
 def test_browser_acceptance_explicitly_confirms_destructive_action(self):
  self.assertIn("dialog.type=='confirm'",BROWSER)
  self.assertIn('Eliminare 2 widget selezionati?',BROWSER)
  self.assertIn('await dialog.accept()',BROWSER)

if __name__=='__main__':unittest.main()
