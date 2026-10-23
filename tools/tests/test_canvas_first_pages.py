from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class CanvasFirstPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = (ROOT / 'apps/api/src/server.ts').read_text()
        cls.web = (ROOT / 'apps/web/src/main.tsx').read_text()

    def test_canvas_page_has_separate_authenticated_endpoint(self):
        self.assertIn("app.post('/api/sessions/:id/pages',requireAuth", self.api)
        self.assertIn("'invalid_page_title'", self.api)
        self.assertIn("'session_closed'", self.api)

    def test_page_insert_preserves_order_and_is_transactional(self):
        self.assertIn("SELECT coalesce(max(position)+1,0)::int AS p FROM activities WHERE session_id=$1", self.api)
        self.assertIn("'slide',$3,'[]'::jsonb", self.api)
        self.assertIn("await cx.query('ROLLBACK').catch(()=>{})", self.api)

    def test_canvas_page_creation_opens_widget_editor(self):
        self.assertIn('async function createCanvasPage()', self.web)
        self.assertIn('beginPageDesign(page)', self.web)
        self.assertIn('onClick={createCanvasPage}', self.web)
        self.assertIn('Crea contenuti con i widget', self.web)
        self.assertNotIn('Nuova pagina con attività (compatibilità)', self.web)
