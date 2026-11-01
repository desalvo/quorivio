"""RC121: fail-closed JSON export with optional in-memory widget properties."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class RC121JsonExport(unittest.TestCase):
 def test_export_omits_only_optional_widget_properties(self):
  source=(ROOT/'apps/web/src/page-draft-recovery.ts').read_text()
  self.assertIn('function exportReadyPageDraft(',source)
  self.assertIn('item!==undefined',source)
  self.assertIn('draft:exportReadyPageDraft(draft),base_draft:exportReadyPageDraft(base)',source)
 def test_invalid_arrays_and_numbers_still_rejected(self):
  source=(ROOT/'apps/web/src/page-draft-recovery.ts').read_text()
  self.assertIn("if(inArray)throw Error('invalid_draft_value')",source)
  self.assertIn("!Number.isFinite(value)",source)
  self.assertIn('validateEditablePageDraft({...draft,widgets:',source)
 def test_download_and_error_message_remain_user_visible(self):
  ui=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn('downloadPageDraftFor(a);setPageExportError',ui)
  self.assertIn('className="page-editor-export-error" role="alert"',ui)
  self.assertIn("setPageExportError('Esportazione non riuscita:",ui)
  css=(ROOT/'apps/web/src/style.css').read_text()
  self.assertIn('.page-editor-thumb-menu .page-editor-export-error',css)
 def test_real_postgres_browser_still_checks_download(self):
  browser=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
  self.assertIn('async with page.expect_download() as download_info:',browser)
  self.assertIn("backup['format']=='quorivio-local-draft-v2'",browser)
  self.assertIn("backup['base_revision']==7",browser)
 def test_node_regression_covers_optional_and_unsafe_values(self):
  tests=(ROOT/'apps/api/test/page-draft-recovery.test.ts').read_text()
  for name in ('31 export omits undefined optional widget props','32 export refuses undefined array elements','33 export refuses invalid nested values','34 export retains prototype-pollution protection','35 export rejects cyclic graph'):
   self.assertIn(name,tests)

if __name__=='__main__':unittest.main()
