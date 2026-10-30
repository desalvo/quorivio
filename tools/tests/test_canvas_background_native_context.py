"""Regression checks for native empty-canvas background context controls."""
from pathlib import Path
import unittest

SOURCE=(Path(__file__).resolve().parents[2]/'apps/web/src/main.tsx').read_text()
CSS=(Path(__file__).resolve().parents[2]/'apps/web/src/style.css').read_text()

class CanvasBackgroundNativeContext(unittest.TestCase):
 def test_only_empty_canvas_opens_background_menu(self):
  self.assertIn('closest(".widget-canvas-item")',SOURCE)
  self.assertIn('setBackgroundMenu(true)',SOURCE)
  self.assertIn('Menu contestuale sfondo canvas',SOURCE)
 def test_background_changes_reuse_existing_layout_handler(self):
  self.assertIn('selectLibraryBackground(id,false)',SOURCE)
  self.assertIn('onBackgroundUpload={file=>{void uploadBackground(file,false)}}',SOURCE)
  self.assertIn('onBackgroundSelect("")',SOURCE)
 def test_existing_widget_menu_is_preserved(self):
  self.assertIn('setContextWidget(onInspectWidget?null:w.id)',SOURCE)
  self.assertIn('onInspectWidget?.(w.id)',SOURCE)
  self.assertIn('.canvas-background-context',CSS)

if __name__=='__main__': unittest.main()
