"""Regression for image-backed live-rendered exports."""
import pathlib
import sys
import tempfile
import unittest
from io import BytesIO
from PIL import Image
from pptx import Presentation
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from visual_export import presenter_steps, image_deck_to_pptx, _safe_capture_url, VIEWERS


class VisualExportTests(unittest.TestCase):
 def test_mapping_and_hidden_presenter_pages(self):
  pages=[{'portable_id':'one','page_design':{'audiencePageId':'hidden'}},
         {'portable_id':'hidden','page_design':{'presenterHidden':True}},
         {'portable_id':'two','page_design':{}}]
  self.assertEqual([x['portable_id'] for x in presenter_steps({'activities':pages})],['one','two'])
  with self.assertRaisesRegex(ValueError,'mapped participant'):
   presenter_steps({'activities':[{'portable_id':'one','page_design':{'audiencePageId':'missing'}}]})
  with self.assertRaises(ValueError):presenter_steps({'activities':[{'portable_id':'same'},{'portable_id':'same'}]})
  self.assertEqual(VIEWERS,{'presenter','participant'})
 def test_capture_origin_is_not_user_controlled_ssrf(self):
  self.assertEqual(_safe_capture_url('http://app:8080'),'http://app:8080')
  self.assertEqual(_safe_capture_url('http://127.0.0.1:8080'),'http://127.0.0.1:8080')
  for url in ['https://example.com:8080','http://u:p@example.com:8080','http://a:80/a','http://foo:9000?q=1','http://foo:9000/#x','http://foo:9000@other:8080']:
   with self.subTest(url=url),self.assertRaises(ValueError):_safe_capture_url(url)
 def test_entire_slide_uses_one_exact_size_png_and_is_in_pptx(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td)
   for i in (1,2):Image.new('RGB',(1280,720),(30*i,20*i,10*i)).save(root/f'{i}.png')
   output=root/'presentation.pptx'
   image_deck_to_pptx([root/'1.png',root/'2.png'],output)
   deck=Presentation(output)
   self.assertEqual(len(deck.slides),2)
   self.assertEqual(len(deck.slides[0].shapes),1)
   s=deck.slides[0].shapes[0]
   self.assertEqual((s.left,s.top,s.width,s.height),(0,0,deck.slide_width,deck.slide_height))
   with self.assertRaises(ValueError):image_deck_to_pptx([root/'1.png'],output)

if __name__=='__main__':unittest.main()
