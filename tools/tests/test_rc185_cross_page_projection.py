"""RC185: fail-closed contracts for independent presenter/audience slides."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
API = (ROOT / 'apps/api/src/server.ts').read_text()
DOMAIN = (ROOT / 'apps/api/src/domain.ts').read_text()
UI = (ROOT / 'apps/web/src/main.tsx').read_text()
SCHEMA = (ROOT / 'apps/api/src/schema.sql').read_text()


class IndependentLivePages(unittest.TestCase):
    def test_participant_receives_only_current_audience_page(self):
        start = API.index('function participantSnapshot(')
        snippet = API[start:API.index('\n}', start) + 2]
        self.assertIn('data.session.current_activity_id', snippet)
        self.assertNotIn('presenter_activity_id', snippet)
        self.assertIn('published?[publicActivity(published)]:[]', snippet)

    def test_one_open_audience_page_and_transactional_cas(self):
        route = API[API.index("app.post('/api/sessions/:id/activities/:aid/open'"):
                    API.index('// A page timer starts')]
        self.assertIn('FOR UPDATE', route)
        self.assertIn('expected_presenter_activity_id', route)
        self.assertIn('page_hidden_from_presenter', route)
        self.assertIn('audienceForPresenter', route)
        self.assertIn("status='closed'", route)
        self.assertIn("status='open'", route)
        self.assertIn('SET current_activity_id=$1,presenter_activity_id=$3', route)
        self.assertIn("await cx.query('COMMIT')", route)
        self.assertIn('await broadcast(req.params.id)', route)

    def test_all_references_enforced_inside_authorized_session(self):
        route = API[API.index("app.patch('/api/sessions/:id/activities/:aid/design'"):
                    API.index("app.post('/api/sessions/:id/activities/:aid/duplicate'")]
        self.assertIn('owner(req.params.id,auth(req)!)', route)
        self.assertIn('SELECT id,page_design FROM activities WHERE session_id=$1', route)
        self.assertIn('audience_page_not_in_session', route)
        self.assertIn('result_source_not_in_session', route)
        self.assertIn('design_revision_conflict', route)
        self.assertIn('validPageDesign', route)

    def test_schema_and_strict_json_fields(self):
        self.assertIn('ADD COLUMN IF NOT EXISTS presenter_activity_id uuid', SCHEMA)
        self.assertIn("'audiencePageId','presenterHidden'", DOMAIN)
        self.assertIn('w.targetActivityId', DOMAIN)

    def test_presenter_navigation_and_editor_canvas_controls(self):
        self.assertIn('presenterVisiblePages(data?.activities||[])', UI)
        self.assertIn('data?.session?.presenter_activity_id||data?.session?.current_activity_id', UI)
        self.assertIn('Pagina partecipanti dal menu canvas', UI)
        self.assertIn('Nascondi al presentatore dal menu canvas', UI)
        self.assertIn('Pagina sorgente statistiche', UI)
        self.assertIn('setPageAudienceId', UI)
        self.assertIn('setPagePresenterHidden', UI)

    def test_private_results_and_portable_ids(self):
        self.assertIn('linkedStatisticContext(widget,activity,activities,widgets)', UI)
        self.assertIn('linkedStatisticActivity(widget,current,activities)', (ROOT/'apps/web/src/widget-results.ts').read_text())
        self.assertIn('sourceActivityId', UI)
        # RC200: slide image assets require a LEFT JOIN, so the page id is qualified.
        self.assertIn('SELECT a.id AS portable_id', API)
        self.assertIn('remapPortablePageRouting', API)
        self.assertIn('unlinkDeletedPage(reference.page_design,req.params.aid)', API)
        self.assertIn('design_revision=design_revision+1', API)


if __name__ == '__main__':
    unittest.main()
