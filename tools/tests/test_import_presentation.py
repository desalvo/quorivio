import importlib.util
import pathlib
import tempfile
import unittest

path=pathlib.Path(__file__).resolve().parents[1]/'import_presentation.py'
spec=importlib.util.spec_from_file_location('presentation_import',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestImport(unittest.TestCase):
 def test_rejects_untrusted_format(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'file.pdf';p.write_bytes(b'bad pdf content')
   with self.assertRaises(ValueError):m.inspect_source(p)
 def test_rejects_wrong_extension(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'file.exe';p.write_bytes(b'123456789')
   with self.assertRaises(ValueError):m.inspect_source(p)
 def test_rejects_fake_pptx(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'file.pptx';p.write_bytes(b'bad fake pptx')
   with self.assertRaises(ValueError):m.inspect_source(p)
 def test_convert_pdf(self):
  try:
   from reportlab.pdfgen.canvas import Canvas
  except ImportError:self.skipTest('reportlab unavailable')
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'test.pdf';c=Canvas(str(p));c.drawString(100,600,'Quorivio import');c.showPage();c.save()
   result=m.convert(p,pathlib.Path(d)/'rendered')
   self.assertEqual(result['page_count'],1)
   self.assertTrue((pathlib.Path(d)/'rendered'/'page-0001.png').exists())
   self.assertTrue((pathlib.Path(d)/'rendered'/'manifest.json').exists())
if __name__=='__main__':unittest.main()
