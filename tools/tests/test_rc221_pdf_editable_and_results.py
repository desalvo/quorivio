"""RC221: converter isolation, mode choice, per-text styles and grading privacy."""
from pathlib import Path
import io
import tempfile
import unittest
from unittest.mock import patch
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from pdf_portable import pdf_to_portable

def assert_private_grading_contract(ui: str, domain: str) -> None:
 """Validate the current result widget without reviving the obsolete footer strip.

 The R button is the sole canvas affordance. The separate configuration switch
 remains inside Widget Formatting and does not expose answer keys to participants.
 """
 required_ui = (
  'Evidenzia le risposte vere nei risultati',
  "className={'result-answer-key-toggle'",
  'hasKey&&<button',
  'setTruthVisible(v=>!v)',
  'resultHasAnswerKey(',
  'resultElementKey(',
  'data-answer-verdict={verdict||undefined}',
 )
 for item in required_ui:
  if item not in ui:
   raise AssertionError('missing result grading contract: '+item)
 for removed in ('Evidenzia le risposte vere sotto la widget risultati',
                 'className="canvas-results-truth-toggle"'):
  if removed in ui:
   raise AssertionError('obsolete footer-overlapping editor control: '+removed)
 for item in ('showCorrectAnswers?:boolean', 'resultTextStyles?:Record'):
  if item not in domain:
   raise AssertionError('missing private grading schema: '+item)

class RC221PDFAndResults(unittest.TestCase):
 def test_pdf_text_is_editable_and_page_positions_are_bounded(self):
  xml=b'''<?xml version="1.0"?><!DOCTYPE pdf2xml SYSTEM "pdf2xml.dtd"><pdf2xml><page number="1" width="1080" height="607"><fontspec id="0" size="24" family="Helvetica" color="#336699"/><text top="100" left="80" width="200" height="30" font="0">Editable PDF heading</text></page></pdf2xml>'''
  def render(_args,timeout=120):
   from pathlib import Path
   Path(_args[-1]+'.xml').write_bytes(xml)
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'slides.pdf';path.write_bytes(b'%PDF-1.4'+b'0'*40)
   with patch('pdf_portable._run',render):
    result,meta=pdf_to_portable(path,Path(tmp)/'media')
   self.assertEqual(meta['editable_text_boxes'],1)
   self.assertTrue(meta['limited_fidelity'])
   self.assertFalse(meta['ocr_performed'])
   self.assertEqual(result['activities'][0]['page_design']['widgets'][0]['kind'],'text')
   self.assertEqual(result['activities'][0]['page_design']['widgets'][0]['style']['color'],'#336699')
 def test_poppler_absolute_image_path_resolves_inside_worker_scratch(self):
  try:
   from PIL import Image
  except ImportError:
   self.skipTest('Pillow is installed in the converter image, not all local Python envs')
  xml=b'<pdf2xml><page number="1" width="1080" height="607"><image top="100" left="80" width="200" height="200" src="/external/path/pages-1_1.png"/></page></pdf2xml>'
  def render(args,timeout=120):
   out=Path(args[-1]);Path(str(out)+'.xml').write_bytes(xml)
   Image.new('RGB',(20,20),'blue').save(out.parent/'pages-1_1.png')
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'slides.pdf';path.write_bytes(b'%PDF-1.4'+b'0'*40)
   with patch('pdf_portable._run',render):
    result,meta=pdf_to_portable(path,Path(tmp)/'media')
   self.assertEqual(meta['editable_images'],1)
   self.assertEqual(result['activities'][0]['page_design']['widgets'][0]['kind'],'image')
   self.assertEqual(len(result['import_assets']),1)
   self.assertTrue((Path(tmp)/'media'/result['import_assets'][0]['id']).is_file())
 def test_pdf_source_and_xml_security_boundaries(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'bad.pdf';path.write_bytes(b'NOTPDF-1.4')
   with self.assertRaisesRegex(ValueError,'signature'):
    pdf_to_portable(path)
 def test_worker_and_api_keep_pdf_editable_in_isolated_job(self):
  worker=(ROOT/'tools/conversion_worker.py').read_text();api=(ROOT/'apps/api/src/server.ts').read_text();docker=(ROOT/'Dockerfile.converter').read_text()
  self.assertIn("pdf_to_portable(source, media_dir=staged_media)",worker)
  self.assertIn("workspace / 'source.pdf'",worker)
  self.assertIn('tools/pdf_portable.py',docker)
  self.assertIn("mime==='application/pdf'?'source.pdf':'source.pptx'",api)
  self.assertIn("if(!await converterAdmissionState().then(state=>state.enabled))",api)
  self.assertIn('scanUploadedFile(received.destination)',api)
 def test_pdf_mode_is_chosen_before_request_and_grading_is_private(self):
  ui=(ROOT/'apps/web/src/main.tsx').read_text();domain=(ROOT/'apps/api/src/domain.ts').read_text()
  self.assertIn('setPendingPresentation({file',ui)
  self.assertIn('Modalità importazione PDF o PowerPoint',ui)
  self.assertIn('Elementi modificabili — conversione parziale',ui)
  assert_private_grading_contract(ui,domain)
  policy=(ROOT/'apps/web/src/live-slide-policy.ts').read_text()
  self.assertIn("['results-button', 'participant-count']",policy)
 def test_no_legacy_automatic_pdf_import_call(self):
  ui=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertNotIn('void importPresentationFile(e.target.files?.[0])',ui)
  self.assertNotIn('void importPresentationFile(f,a.id)',ui)

if __name__=='__main__':unittest.main()
