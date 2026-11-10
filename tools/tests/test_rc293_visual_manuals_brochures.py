#!/usr/bin/env python3
"""RC293: keep publication truly graphical, compact, provenance-aware and bilingual."""
from __future__ import annotations
import hashlib,re,unittest
from pathlib import Path
import fitz
from PIL import Image
from tools.manual_screenshot_catalog import evidence,LATEST_ARCHIVED_SCREENSHOTS,LATEST_ARCHIVED_COMMIT
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'docs/manuals-src'
ROLE={'user':'user','presenter':'presenter','admin':'admin'}

class RC293VisualManualsAndBrochures(unittest.TestCase):
 def test_icon_atlases_are_real_screenshot_derived_and_bilingual(self):
  evidence(LATEST_ARCHIVED_SCREENSHOTS,expected_commit=LATEST_ARCHIVED_COMMIT,minimum=25)
  source=(ROOT/'tools/manual_icon_atlas.py').read_text()
  self.assertIn('manual-evidence-rc291/editor-canvas.png',str((ROOT/'docs/assets/manual-evidence-rc291/editor-canvas.png').resolve()))
  self.assertIn("SCREEN=ROOT/'docs/assets/manual-evidence-rc291/editor-canvas.png'",source)
  for language in ('it','en'):
   img=ROOT/f'docs/assets/manual-illustrations/editor-toolbar-atlas-{language}-rc293.png'
   with Image.open(img) as pic:
    self.assertGreater(pic.width,1400)
    self.assertGreater(pic.height,1100)
  self.assertEqual(len(__import__('tools.manual_icon_atlas',fromlist=['NAMES']).NAMES),20)

 def test_six_manuals_contain_real_figures_and_no_commit_id(self):
  for role in ROLE:
   for language in ('it','en'):
    with self.subTest(role=role,language=language):
     source=(SOURCE/f'{role}-guide.{language}.md').read_text()
     self.assertIn('RC293',source)
     self.assertIn('../assets/manual-evidence-rc291/',source)
     path=ROOT/f'docs/manuals/{role}-guide.{language}.pdf'
     copy=ROOT/f'apps/web/public/docs/manuals/{role}-guide.{language}.pdf'
     self.assertEqual(hashlib.sha256(path.read_bytes()).digest(),hashlib.sha256(copy.read_bytes()).digest())
     with fitz.open(path) as pdf:
      self.assertGreaterEqual(pdf.page_count,16)
      self.assertLessEqual(pdf.page_count,40)
      texts='\n'.join(page.get_text() for page in pdf)
      self.assertIn('RC293',texts)
      self.assertIn('Alessandro De Salvo',texts)
      self.assertIn('braket71@gmail.com',texts)
      self.assertIn('EUPL-1.2',texts)
      self.assertNotRegex(texts,r'\b[0-9a-f]{40}\b')
      self.assertFalse(any(not page.get_image_info() for page in pdf),'Every page requires a visible photographic or screenshot component')
      self.assertIn('RC291',texts)
      self.assertNotIn('<figure',texts)

 def test_editor_explanations_and_synthetic_photo_attribution(self):
  for language in ('it','en'):
   presenter=(SOURCE/f'presenter-guide.{language}.md').read_text()
   atlas=f'editor-toolbar-atlas-{language}-rc293.png'
   self.assertIn(atlas,presenter)
   self.assertIn('editor-widget-format-tabs.png',presenter)
   self.assertIn('rehearsal-side-by-side-smartphone.png',presenter)
   for role in ('admin','user'):
    self.assertIn('editorial-', (SOURCE/f'{role}-guide.{language}.md').read_text())
  finisher=(ROOT/'tools/manual_visual_finishing.py').read_text()
  self.assertIn('VERIFIED ARCHIVED SCREENSHOT',finisher)
  self.assertIn('SYNTHETIC EDITORIAL PHOTOGRAPH',finisher)
  css=(ROOT/'tools/generate_manuals.py').read_text()
  self.assertIn('break-before:auto',css)
  self.assertNotIn('break-before:page',css)

 def test_two_brochures_have_two_searchable_pages_and_release_metadata(self):
  for language in ('it','en'):
   pdf=ROOT/f'docs/brochures/quorivio-brochure-{language}.pdf'
   copy=ROOT/f'apps/web/public/docs/brochures/quorivio-brochure-{language}.pdf'
   self.assertEqual(pdf.read_bytes(),copy.read_bytes())
   with fitz.open(pdf) as doc:
    self.assertEqual(doc.page_count,2)
    for page in doc:self.assertGreaterEqual(len(page.get_image_info()),1)
    t='\n'.join(p.get_text() for p in doc)
    for word in ('Quorivio','RC293','Alessandro De Salvo','braket71@gmail.com','EUPL-1.2','github.com/desalvo/quorivio','.quo'):
     self.assertIn(word,t)
    self.assertNotRegex(t,r'\b[0-9a-f]{40}\b')
  self.assertIn('official-quorivio-logo.png',(ROOT/'tools/generate_brochures.py').read_text())

 def test_ci_and_source_release_guard_references(self):
  ci=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('verify_rc_cycle292_inventory.py --historical',ci)
  self.assertIn('verify_rc_cycle293_inventory.py',ci)
  self.assertIn('test_rc293_visual_manuals_brochures',ci)
  from tools.manual_release_metadata import metadata
  m=metadata()
  self.assertEqual(m['build'],'RC293')
  self.assertEqual(m['published'],'2026-11-10')

if __name__=='__main__':unittest.main()
