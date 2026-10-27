"""RC regression: keyboard page reordering, focus restore and audible state.

Real native drag/drop and interaction are covered by existing browser acceptance;
these checks ensure the alternative never loses the unsaved-change fence.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

class ThumbnailKeyboardRC(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tsx=(ROOT/'apps/web/src/main.tsx').read_text()
  cls.css=(ROOT/'apps/web/src/style.css').read_text()
 def test_keyboard_reordering_uses_server_endpoint_and_draft_guard(self):
  self.assertIn('aria-keyshortcuts="Alt+ArrowUp Alt+ArrowDown"',self.tsx)
  self.assertIn("if(e.altKey){if((e.key==='ArrowUp'||e.key==='ArrowDown')&&to!==i)void dropPage(a.id,pages[to].id);return}",self.tsx)
  self.assertIn('sourceId===targetId||!confirmPageNavigation()',self.tsx)
  self.assertIn("await request(`/sessions/${sessionId}/pages/order`,'PUT',{activity_ids:activityIds})",self.tsx)
 def test_navigation_is_distinct_from_reordering(self):
  self.assertIn("if(pages[to]){beginPageDesign(pages[to]);requestAnimationFrame",self.tsx)
  self.assertIn('onClick={()=>beginPageDesign(a)}',self.tsx)
 def test_menu_escape_restores_keyboard_focus(self):
  self.assertIn("e.key==='Escape'){e.preventDefault();e.stopPropagation();setPageThumbMenu('')",self.tsx)
  self.assertIn('requestAnimationFrame(()=>trigger?.focus())',self.tsx)
 def test_page_order_announced_on_completion_failure_and_pending(self):
  for value in ('Riordino delle pagine in corso','Ordine delle pagine salvato','Riordino non riuscito, ordine precedente conservato'):
   self.assertIn(value,self.tsx)
  self.assertIn('className="page-editor-order-status" role="status" aria-live="polite"',self.tsx)
  self.assertIn('clip:rect(0,0,0,0)',self.css)
 def test_no_dangerous_force_click_or_dom_reorder(self):
  self.assertNotIn('force: true',self.tsx)
  self.assertIn('movePageId(snap.activities.map(a=>a.id),sourceId,targetId)',self.tsx)

if __name__=='__main__':unittest.main()
