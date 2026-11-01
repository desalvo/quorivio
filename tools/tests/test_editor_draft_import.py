"""Wiring checks only: real browser acceptance runs under browser_test=true."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[2]
MAIN=(R/'apps/web/src/main.tsx').read_text()
REC=(R/'apps/web/src/page-draft-recovery.ts').read_text()
BROWSER=(R/'tools/ci_browser_editor_postgres.py').read_text()
class EditorDraftImport(unittest.TestCase):
 def test_export_is_v2_with_baseline(self):self.assertIn("format:'quorivio-local-draft-v2'",REC);self.assertIn('createPageDraftBackup(selected,designActivity',MAIN)
 def test_explicit_file_upload(self):self.assertIn('type="file" accept=".json,application/json"',MAIN)
 def test_user_confirmation(self):self.assertIn('window.confirm(plan.mode',MAIN)
 def test_no_automatic_local_storage(self):self.assertNotIn('localStorage',REC);self.assertNotIn('sessionStorage',REC)
 def test_stale_requires_reconciliation(self):self.assertIn("plan.mode==='reconcile'",MAIN);self.assertIn('base:backup.base_draft,local:backup.draft',MAIN)
 def test_server_freshness(self):self.assertIn('latestPageDraft.current!==signature',MAIN);self.assertIn('loadedDesignRevision.current=revision',MAIN)
 def test_recovery_never_calls_save(self):self.assertNotIn('updatePageDesign()',MAIN[MAIN.index('async function importPageDraft('):MAIN.index('const pageHasUnsavedChanges=')])
 def test_browser_covers_import_export_and_stale_merge(self):
     self.assertIn('page.expect_download()',BROWSER)
     self.assertIn('Esporta layout JSON',BROWSER)
     self.assertIn("await expect(editor.get_by_text('Conflitto di revisione'))",BROWSER)
     self.assertIn("choice.select_option('local')",BROWSER)
if __name__=='__main__':unittest.main()
