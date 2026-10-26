"""Regression checks for the empty page SQL and editor navigation wiring."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API = (ROOT/'apps/api/src/server.ts').read_text()
WEB = (ROOT/'apps/web/src/main.tsx').read_text()
CSS = (ROOT/'apps/web/src/style.css').read_text()

class FullPageEditorTests(unittest.TestCase):
    def test_empty_page_insert_bindings(self):
        body = API.split("app.post('/api/sessions/:id/pages',",1)[1].split("// Images already",1)[0]
        stmt = re.search(r'INSERT INTO activities.*?VALUES\((.*?)\)"\s*,\s*\[([^\]]+)\]',body,re.S)
        self.assertIsNotNone(stmt)
        placeholders = {int(v) for v in re.findall(r'\$(\d+)',stmt.group(1))}
        self.assertEqual(placeholders,{1,2,3,4})
        self.assertEqual(len(stmt.group(2).split(',')),4)
    def test_deletion_is_authorized_and_broadcast(self):
        section=API.split("app.delete('/api/sessions/:id/pages/:aid'",1)[1].split('// Canvas-first pages',1)[0]
        self.assertIn('session_presenters',section)
        self.assertIn('DELETE FROM activities',section)
        self.assertIn('current_activity_id=NULL',section)
        self.assertIn('await broadcast(req.params.id)',section)
    def test_editor_navigation_and_actions(self):
        for text in ['page-editor-sidebar','page-editor-thumbnails','page-editor-thumb-menu','deleteCanvasPage','duplicatePage','Modifica le pagine','editor-widget-rail']:
            self.assertIn(text,WEB)
        self.assertIn('position:fixed!important;inset:0',CSS)
        self.assertIn('overflow-y:auto',CSS)

if __name__=='__main__':unittest.main()
