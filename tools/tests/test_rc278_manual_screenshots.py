"""RC278: checked-in author metadata and no fake 'real' screenshot evidence."""
import hashlib
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from manual_release_metadata import metadata,validate_release
from manual_screenshot_catalog import evidence,CATALOG,CAPTIONS,gallery,validate_capture_environment


class ManualScreenshotContracts(unittest.TestCase):
 def test_author_version_logo_and_publication_are_grounded(self):
  meta=metadata(ROOT,commit='a'*40)
  validate_release(meta)
  self.assertEqual(meta['version'],json.loads((ROOT/'package.json').read_text())['version'])
  self.assertEqual(meta['license'],'EUPL-1.2')
  self.assertIn(meta['email'],(ROOT/'LICENSE').read_text())
  self.assertIn(meta['cycle'],meta['build'])
  self.assertEqual(meta['published'],'2026-11-09')
  self.assertTrue((ROOT/'docs/assets/quorivio-logo.svg').is_file())
  self.assertIn('github.com/desalvo/quorivio',meta['repository'])
  workflow=(ROOT/'.github/workflows/ci.yml').read_text()
  active=re.findall(r'(?m)^\s*python3 tools/verify_rc_cycle(\d+)_inventory\.py\s*$',workflow)
  self.assertEqual(meta['cycle'],'RC'+active[-1], 'New release must update the manual build identifier too')

 def test_real_shots_require_positive_provenance_and_exact_hash(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d);file=path/'login-desktop.png'
   file.write_bytes(b'\x89PNG\r\n\x1a\nunit test fixture')
   manifest={'source':'illustration','fixture':'synthetic-only','commit':'a'*40,
      'shots':{'login-desktop':{'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'width':1440,'height':900}}}
   (path/'capture.json').write_text(json.dumps(manifest))
   with self.assertRaisesRegex(ValueError,'provenance'):evidence(path,minimum=1)
   manifest['source']='disposable-postgresql-chromium-live-app'
   (path/'capture.json').write_text(json.dumps(manifest))
   with self.assertRaisesRegex(ValueError,'commit mismatch'):evidence(path,expected_commit='b'*40,minimum=1)
   file.write_bytes(file.read_bytes()+b'change')
   with self.assertRaisesRegex(ValueError,'checksum mismatch'):evidence(path,minimum=1)

 def test_disposable_origin_only_and_no_real_customer_accounts(self):
  from unittest.mock import patch
  with patch.dict('os.environ',{'QUORIVIO_CI_BASE_URL':'https://example.org','QUORIVIO_CI_ADMIN_EMAIL':'someone@example.com','QUORIVIO_CI_NEW_PASSWORD':'x','QUORIVIO_CI_LOAD_TOKEN':'x'}):
   with self.assertRaises(ValueError):validate_capture_environment()
  with patch.dict('os.environ',{'QUORIVIO_CI_ADMIN_EMAIL':'real@company.org','QUORIVIO_CI_NEW_PASSWORD':'x','QUORIVIO_CI_LOAD_TOKEN':'x'}):
   with self.assertRaises(RuntimeError):validate_capture_environment()

 def test_each_role_has_gallery_and_practical_workflows(self):
  for lang in ('it','en'):
   for role in ('user','presenter','admin'):
    text=(ROOT/f'docs/manuals-src/{role}-guide.{lang}.md').read_text()
    self.assertIn('<!-- REAL_SCREENSHOT_GALLERY -->',text)
    self.assertIn(metadata(ROOT)['cycle'],text)
    self.assertGreaterEqual(text.count('\n## '),18)
    self.assertGreaterEqual(len([k for k,v in CATALOG.items() if role in v]),4)
  for term in ('Disaster Recovery','RPO','RTO','pg_restore','replicaCount','ReadWriteMany','backup'):
   self.assertIn(term,(ROOT/'docs/manuals-src/admin-guide.en.md').read_text())
  for term in ('DR','RPO','RTO','pg_restore','replicaCount','ReadWriteMany','backup'):
   self.assertIn(term,(ROOT/'docs/manuals-src/admin-guide.it.md').read_text())

 def test_ci_acquires_live_not_dom_mock_and_uploads_all_six(self):
  workflow=(ROOT/'.github/workflows/ci.yml').read_text()
  capture=(ROOT/'tools/ci_manual_real_screenshots.py').read_text()
  publisher=(ROOT/'tools/generate_manuals.py').read_text()
  self.assertIn('python3 tools/ci_manual_real_screenshots.py',workflow)
  self.assertIn('generate_manuals.py --require-real',workflow)
  self.assertIn('quorivio-live-manuals-',workflow)
  self.assertIn('capture.json',capture)
  self.assertIn('from ci_browser_participant import prepare, enter, vote',capture)
  self.assertIn("validated",'validated')
  self.assertIn('gallery(role, lang, require=require_real',publisher)

if __name__=='__main__':unittest.main()
