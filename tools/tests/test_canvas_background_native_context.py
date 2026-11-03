"""Regression checks for native empty-canvas background context controls."""
from pathlib import Path
import unittest

SOURCE=(Path(__file__).resolve().parents[2]/'apps/web/src/main.tsx').read_text()
CSS=(Path(__file__).resolve().parents[2]/'apps/web/src/style.css').read_text()

class CanvasBackgroundNativeContext(unittest.TestCase):
 def test_only_empty_canvas_opens_background_menu(self):
  self.assertIn("target.closest('.widget-canvas-item')",SOURCE)
  self.assertIn('onContextMenuCapture={handleCanvasContext}',SOURCE)
  self.assertIn('canvasWidgetAtPoint(canvas,e.clientX,e.clientY)',SOURCE)
  self.assertIn('setBackgroundMenu(true)',SOURCE)
  self.assertIn('Menu contestuale sfondo canvas',SOURCE)
 def test_background_changes_reuse_existing_layout_handler(self):
  self.assertIn('selectLibraryBackground(id,false)',SOURCE)
  # The menu still calls the existing upload handler, passing the active
  # device so a smartphone image cannot replace the desktop background.
  self.assertIn("onBackgroundUpload={file=>uploadBackground(file,false,canvasDevice==='phone')}",SOURCE)
  self.assertIn("backgroundAssetId={canvasDevice==='phone'?mobileLayoutDraft.backgroundAssetId||'':questionBackgroundAsset}",SOURCE)
  self.assertIn('if(forMobile){setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));}',SOURCE)
  self.assertIn("else{setQuestionBackgroundAsset(applied.id);setQuestionBackground('')}",SOURCE)
  self.assertIn('onBackgroundSelect("")',SOURCE)
 def test_existing_widget_menu_is_preserved(self):
  # Widget context is now opened by the shared hit-tested floating menu,
  # not by automatically invoking the Properties dialog during right-click.
  self.assertIn('openWidgetContextMenu(widgetId,widget,e.clientX,e.clientY)',SOURCE)
  self.assertIn('setContextWidget(widgetId)',SOURCE)
  self.assertIn('onContextMenuCapture={handleCanvasContext}',SOURCE)
  self.assertIn('onInspectWidget?.(w.id)',SOURCE)
  self.assertIn('.canvas-background-context',CSS)

if __name__=='__main__': unittest.main()
