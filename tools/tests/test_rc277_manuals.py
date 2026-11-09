"""Dependency-free RC277 bilingual manual publication and coverage guard."""
import unittest
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'docs/manuals-src'
PDF=ROOT/'docs/manuals'
WEB=ROOT/'apps/web/public/docs/manuals'

class ManualsRC277(unittest.TestCase):
 def test_six_manuals_have_matching_published_copies(self):
  for role in ('user','presenter','admin'):
   for language in ('it','en'):
    with self.subTest(role=role,language=language):
     name=f'{role}-guide.{language}.pdf'
     original=PDF/name;published=WEB/name
     self.assertGreater(original.stat().st_size,20000)
     self.assertEqual(original.read_bytes()[:5],b'%PDF-')
     self.assertEqual(hashlib.sha256(original.read_bytes()).digest(),hashlib.sha256(published.read_bytes()).digest())
 def test_editable_bilingual_sources_and_full_widget_catalog(self):
  for language in ('it','en'):
   role_sources={r:(SOURCE/f'{r}-guide.{language}.md').read_text(encoding='utf8') for r in ('user','presenter','admin')}
   for r,content in role_sources.items():
    self.assertIn('RC277',content)
    self.assertGreaterEqual(content.count('\n## '),18)
    self.assertIn('manual-illustrations/',content)
   presenter=role_sources['presenter']
   for kind in ('title','footer','text','postit','divider','shape','line','image','logo','video','pdf','qr','profile','question','timed-quiz','topic-question','rating','reactions','results-button','participant-count','timer'):
    self.assertIn('`'+kind+'`',presenter)
   admin=role_sources['admin']
   for topic in ('PostgreSQL 18','LDAP','S3','WebDAV','NFS','POSIX','MFA','audit','ClamAV','RPO/RTO'):
    self.assertIn(topic,admin)
 def test_illustrative_not_fake_live_screen_captures(self):
  for role in ('user','presenter','admin'):
   for lang in ('it','en'):
    content=(SOURCE/f'{role}-guide.{lang}.md').read_text()
    self.assertTrue('ricostruzioni' in content.lower() or 'reconstructions' in content.lower())
  for name in ('sessions','editor','results','participant','backup','ldap','sample-bar-chart','sample-pie-chart','backup-lifecycle','ldap-approval'):
   self.assertTrue((ROOT/f'docs/assets/manual-illustrations/{name}.png').is_file())
 def test_publication_is_explicit_and_no_runtime_side_effects(self):
  generator=(ROOT/'tools/generate_manuals.py').read_text(encoding='utf8')
  self.assertIn('if __name__',generator)
  self.assertIn('SOURCE',generator)
  self.assertIn('WEB',generator)
  workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
  self.assertIn('tools.tests.test_rc277_manuals',workflow)

if __name__=='__main__': unittest.main()
