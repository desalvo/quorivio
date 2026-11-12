"""RC119: content overflow excludes out-of-bounds widget resize chrome."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class RC119ContentOnlyAutoFit(unittest.TestCase):
 def test_content_only_measurement(self):
  # RC326 supersedes the legacy height-expanding autofit. The new fit
  # mechanism measures only the inner frame and content, not resize handles
  # on the outer widget, and never changes the persisted widget geometry.
  source=(ROOT/'apps/web/src/main.tsx').read_text()
  component=source.split('function WidgetContentFit({',1)[1].split('type DiskVolumeStatus=',1)[0]
  self.assertIn('const a=frame.current,b=body.current',component)
  self.assertIn('const next=proportionalWidgetScale({',component)
  self.assertIn('contentWidth:Math.max(b.scrollWidth,b.clientWidth)',component)
  self.assertIn('contentHeight:Math.max(b.scrollHeight,b.clientHeight)',component)
  self.assertIn('frameWidth:a.clientWidth,frameHeight:a.clientHeight',component)
  self.assertIn('data-fit-mode={allowScale?',component)
  self.assertIn("autoFit is a content-fit preference, NEVER a widget geometry edit",source)
  self.assertNotIn('autoFitExpandedPosition(',source)
  self.assertNotIn('const overflow=node.scrollHeight-node.clientHeight',source)
 def test_browser_checks_geometry_before_click_and_rejection_before_count(self):
  s=(ROOT/'tools/ci_browser_editor.py').read_text()
  self.assertLess(s.index('fixture_geometry=await'),s.index("await click_canvas_tool(page,'Duplica selezione')"))
  self.assertLess(s.index("assert not duplication_alerts, ('Group duplication rejected:"),s.index("to_have_count(5)",s.index("await click_canvas_tool(page,'Duplica selezione')")))
  self.assertIn("await expect(page.locator('.widget-canvas-item')).to_have_count(3)",s)
 def test_chrome_guards_are_outside_content_frame(self):
  s=(ROOT/'apps/web/src/style.css').read_text()
  self.assertIn('bottom:0!important',s)
  self.assertIn('.widget-fit-frame',s)
  self.assertIn('position:absolute!important',s)
