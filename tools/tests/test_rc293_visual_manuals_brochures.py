#!/usr/bin/env python3
"""RC293: keep publication truly graphical, compact, provenance-aware and bilingual."""
from __future__ import annotations
import ast,hashlib,re,unittest
from pathlib import Path
import fitz
from tools.manual_screenshot_catalog import evidence,LATEST_ARCHIVED_SCREENSHOTS,LATEST_ARCHIVED_COMMIT
from tools.manual_release_metadata import metadata
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
   # PyMuPDF is already provisioned in the early PDF gate. Its pixmap
   # decoder validates the entire PNG without requiring Pillow on runners.
   pic=fitz.Pixmap(str(img))
   self.assertGreater(pic.width,1400)
   self.assertGreater(pic.height,1100)
   self.assertIn(pic.n,(3,4))
  # Parse the editor icon legend as a source constant instead of importing
  # the image-generation tool, which intentionally depends on Pillow.
  atlas_tree=ast.parse((ROOT/'tools/manual_icon_atlas.py').read_text())
  names=next(node.value for node in atlas_tree.body
             if isinstance(node,ast.Assign)
             and any(isinstance(target,ast.Name) and target.id=='NAMES' for target in node.targets))
  self.assertEqual(len(ast.literal_eval(names)),20)

 def test_six_manuals_contain_real_figures_and_no_commit_id(self):
  for role in ROLE:
   for language in ('it','en'):
    with self.subTest(role=role,language=language):
     source=(SOURCE/f'{role}-guide.{language}.md').read_text()
     self.assertIn(metadata()['build'],source)
     self.assertIn('../assets/manual-evidence-rc291/',source)
     path=ROOT/f'docs/manuals/{role}-guide.{language}.pdf'
     copy=ROOT/f'apps/web/public/docs/manuals/{role}-guide.{language}.pdf'
     self.assertEqual(hashlib.sha256(path.read_bytes()).digest(),hashlib.sha256(copy.read_bytes()).digest())
     with fitz.open(path) as pdf:
      self.assertGreaterEqual(pdf.page_count,16)
      self.assertLessEqual(pdf.page_count,40)
      texts='\n'.join(page.get_text() for page in pdf)
      self.assertIn(metadata()['build'],texts)
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

 def test_two_brochures_have_six_searchable_pages_and_release_metadata(self):
  for language in ('it','en'):
   pdf=ROOT/f'docs/brochures/quorivio-brochure-{language}.pdf'
   copy=ROOT/f'apps/web/public/docs/brochures/quorivio-brochure-{language}.pdf'
   self.assertEqual(pdf.read_bytes(),copy.read_bytes())
   with fitz.open(pdf) as doc:
    self.assertEqual(doc.page_count,6)
    for page in doc:self.assertTrue(page.get_image_info() or len(page.get_drawings())>=12)
    t='\n'.join(p.get_text() for p in doc)
    for word in ('Quorivio','RC333','Alessandro De Salvo','braket71@gmail.com','EUPL-1.2','github.com/desalvo/quorivio','.quo'):
     self.assertIn(word,t)
    self.assertNotRegex(t,r'\b[0-9a-f]{40}\b')
  self.assertIn('mock-reference-6-pages-2026-11.jpg',(ROOT/'tools/generate_brochures.py').read_text())

 def test_ci_and_source_release_guard_references(self):
  ci=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('verify_rc_cycle292_inventory.py --historical',ci)
  self.assertIn('verify_rc_cycle293_inventory.py',ci)
  self.assertIn('test_rc293_visual_manuals_brochures',ci)
  from tools.manual_release_metadata import metadata
  m=metadata()
  from tools.verify_rc_current_inventory import current_verifier_module
  active=current_verifier_module().__name__.removeprefix('verify_rc_cycle').removesuffix('_inventory')
  self.assertEqual(m['build'],f'RC{active}')
  self.assertEqual(m['published'],'2026-11-10')

if __name__=='__main__':unittest.main()
