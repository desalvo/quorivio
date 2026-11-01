"""RC103: native PowerPoint QR is scannable, linked, bounded and private to export."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from pptx_portable import portable_to_pptx

URL='https://quorivio.example.org/join/AbCdEfGh0123456789_-ABCD'

def definition(url=URL, kinds=('qr',)):
    return {'format':'quorivio-session','version':1,
            'session':{'title':'Workshop','participant_join_url':url},
            'activities':[{'type':'slide','title':'Pagina 1', 'page_design':{'widgets':[
                {'id':f'w{i}', 'kind':kind,'label':'Accesso partecipanti',
                 'position':{'x':20+i*30,'y':15,'width':26,'height':58}}
                for i,kind in enumerate(kinds)]}}]}

class ParticipantQrPowerpoint(unittest.TestCase):
    def test_scannable_png_with_clickable_and_editable_url(self):
        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        from PIL import Image
        import io
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'qr.pptx'
            portable_to_pptx(definition(),target)
            shapes=Presentation(target).slides[0].shapes
            self.assertEqual(len(shapes),2)
            picture,link=shapes[0],shapes[1]
            self.assertEqual(picture.shape_type,MSO_SHAPE_TYPE.PICTURE)
            self.assertEqual(picture.width,picture.height)
            self.assertEqual(link.text,URL)
            self.assertEqual(link.text_frame.paragraphs[0].runs[0].hyperlink.address,URL)
            self.assertGreater(link.top,picture.top)
            with Image.open(io.BytesIO(picture.image.blob)) as img:
                self.assertEqual(img.format,'PNG')
                self.assertGreater(img.size[0],100)
                self.assertLess(img.size[0],2000)
                self.assertEqual(img.size[0],img.size[1])
                self.assertEqual(img.convert('L').getextrema(), (0, 255))

    def test_repeated_widget_uses_same_link_on_each_slide(self):
        from pptx import Presentation
        with tempfile.TemporaryDirectory() as d:
            data=definition()
            data['activities'].append(data['activities'][0].copy())
            path=Path(d)/'repeated.pptx'
            portable_to_pptx(data,path)
            deck=Presentation(path)
            self.assertEqual(len(deck.slides),2)
            for slide in deck.slides:
                self.assertEqual(slide.shapes[1].text,URL)

    def test_missing_or_untrusted_url_fails_closed(self):
        for url in (None,'','/join/AbCdEfGh0123456789_-ABCD',
                    'javascript:alert(1)',
                    'https://user:password@quorivio.example.org/join/AbCdEfGh0123456789_-ABCD',
                    'https://quorivio.example.org/screen/AbCdEfGh0123456789_-ABCD',
                    'https://quorivio.example.org/join/AbCdEfGh0123456789_-ABCD?next=https://evil.example',
                    'https://quorivio.example.org/join/AbCdEfGh0123456789_-ABCD#fragment',
                    'https://quorivio.example.org/join/AbCdEfGh0123456789_-ABCD\nBad:header',
                    'file:///join/AbCdEfGh0123456789_-ABCD'):
            with self.subTest(url=url), tempfile.TemporaryDirectory() as d:
                with self.assertRaises(ValueError):
                    portable_to_pptx(definition(url),Path(d)/'bad.pptx')

    def test_api_does_not_persist_participant_secret_in_generic_json(self):
        s=(ROOT/'apps/api/src/server.ts').read_text()
        self.assertIn('const exportHasQr=pptxDefinition.activities.some',s)
        self.assertIn('pptxDefinition.session.participant_join_url=',s)
        self.assertIn('const portable=JSON.stringify(pptxDefinition)',s)
        self.assertNotIn('participant_join_url',s.split('async function portableSession(id:string)',1)[1].split('\n',1)[0])
        self.assertIn('qrcode==8.2',(ROOT/'Dockerfile.converter').read_text())

if __name__=='__main__':unittest.main()
