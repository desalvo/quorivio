"""Source/CI contracts; runtime truth is checked by ci_editor_postgres.py."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
SCHEMA=(ROOT/'apps/api/src/schema.sql').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text()
REAL=(ROOT/'tools/ci_editor_postgres.py').read_text()
BROWSER=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()

class EditorPostgresConcurrencyContracts(unittest.TestCase):
 def test_independent_design_revision_column(self):self.assertIn('design_revision integer NOT NULL DEFAULT 1',SCHEMA)
 def test_row_lock_serializes_concurrent_saves(self):self.assertIn('design_revision FROM activities',API);self.assertIn('FOR UPDATE',API)
 def test_api_rejects_invalid_expected_revision(self):self.assertIn("error:'invalid_design_revision'",API)
 def test_api_reports_stale_revision_without_overwrite(self):self.assertIn("error:'design_revision_conflict'",API)
 def test_api_increments_revision_atomically(self):self.assertIn('design_revision=design_revision+1',API)
 def test_api_returns_new_revision(self):self.assertIn('design_revision:saved.rows[0].design_revision',API)
 def test_ui_sends_expected_revision(self):self.assertIn('expected_design_revision:loadedDesignRevision.current',UI)
 def test_ui_preserves_unsaved_draft_on_conflict(self):self.assertIn('setPageConflict(true)',UI);self.assertIn('Le modifiche locali non sono state sovrascritte',UI)
 def test_ui_requires_confirmation_to_discard_conflicted_draft(self):self.assertIn('Scartare le modifiche locali',UI)
 def test_ui_disables_save_while_conflicted(self):self.assertIn('pageSavePending||pageConflict',UI)
 def test_ui_loaded_signature_includes_background_colors(self):self.assertIn('serializePageDraft(pageDraftFromActivity(x))',UI)
 def test_real_postgres_http_gate_is_mandatory(self):self.assertIn('run: python3 tools/ci_editor_postgres.py',WORKFLOW)
 def test_real_browser_is_opt_in(self):
  self.assertIn('python3 tools/ci_browser_editor_postgres.py',WORKFLOW)
  self.assertIn("if: github.event_name == 'workflow_dispatch' && inputs.browser_test",WORKFLOW)
  self.assertIn('name: Chromium editor PostgreSQL persistence and conflict acceptance (opt-in)',WORKFLOW)
 def test_browser_does_not_mock_routes(self):self.assertNotIn('.route(',BROWSER)
 def test_browser_tests_real_db_reload(self):self.assertIn("await call(context,'GET',f'/api/sessions/{sid}')",BROWSER)
 def test_independent_slide_uses_canvas_pages_endpoint(self):
  self.assertIn("second=api(a,'POST',path+'/pages',{'title':'Independent'},201)",REAL)
  self.assertIn("app.post('/api/sessions/:id/pages'",API)
  self.assertNotIn("'type':'slide','options':[]",REAL)
 def test_concurrent_http_test_has_two_real_writers(self):self.assertIn('ThreadPoolExecutor(max_workers=2)',REAL)
 def test_test_scripts_refuse_remote_servers(self):self.assertIn("'127.0.0.1'",REAL);self.assertIn("'127.0.0.1'",BROWSER)
 def test_browser_artifacts_contain_no_cookie_dump(self):self.assertNotIn('storage_state(',BROWSER)
