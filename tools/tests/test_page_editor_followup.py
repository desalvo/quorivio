"""Guard page editor UX fixes: copy selection, keyboard navigation and immutable closed sessions."""
from pathlib import Path
import unittest

UI = (Path(__file__).resolve().parents[2] / 'apps/web/src/main.tsx')

class PageEditorFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui = UI.read_text(encoding='utf-8')

    def test_duplicate_opens_newly_created_page(self):
        self.assertIn('const previousIds=new Set(snap?.activities.map(a=>a.id)||[])', self.ui)
        self.assertIn('const copy=updated.activities.find(a=>!previousIds.has(a.id))', self.ui)
        self.assertIn('if(copy)beginPageDesign(updated.activities.find(a=>a.id===copy.id)||copy)', self.ui)
        self.assertIn('ids.splice(at+1,0,copy.id)', self.ui)

    def test_thumbnail_keyboard_selection(self):
        self.assertIn("['ArrowUp','ArrowDown','Home','End']", self.ui)
        self.assertIn("requestAnimationFrame(()=>document.querySelectorAll<HTMLButtonElement>('.page-editor-thumb')[to]?.focus())",self.ui)

    def test_closed_session_actions_disabled(self):
        self.assertIn("{snap.session.status!=='closed'&&<>",self.ui)
        for action in ('Nuova pagina prima','Nuova pagina dopo','Duplica pagina','Sposta su','Sposta giù','Elimina pagina'):
            self.assertIn(action,self.ui)
        self.assertIn("draggable={snap.session.status!=='closed'&&!pageOrderPending}",self.ui)

if __name__ == '__main__':
    unittest.main()
