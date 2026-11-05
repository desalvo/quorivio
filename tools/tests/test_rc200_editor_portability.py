"""RC200: editor import/export, privacy and raster-slide preservation contracts."""
from __future__ import annotations
import io
import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from pptx_portable import portable_to_pptx, _validate_export_input


class RC200EditorPortability(unittest.TestCase):
    def test_editor_context_import_and_compact_header(self):
        web = (ROOT / 'apps/web/src/main.tsx').read_text()
        self.assertIn('editor-mock-meta', web)
        self.assertIn('Proprietario primario:', web)
        self.assertIn('editor-thumb-import', web)
        self.assertIn('Importa PDF/PPTX', web)
        self.assertIn('persistPageOrder', web)
        self.assertIn('statisticsAnonymize', web)
        self.assertIn('export.xlsx?anonymize=', web)
        self.assertIn('export.pdf', web)

    def test_stats_owner_safeguard_and_export_endpoints(self):
        api = (ROOT / 'apps/api/src/server.ts').read_text()
        self.assertIn("session.owner_id!==auth(req)", api)
        self.assertIn('const anonymize=requested!==\'0\'', api)
        self.assertIn("'/api/sessions/:id/export.xlsx'", api)
        self.assertIn("'/api/sessions/:id/export.pdf'", api)
        self.assertIn('slide_asset_id', api)
        self.assertIn('slide_asset_id?[a.slide_asset_id]:[]', api)
        bundle = (ROOT / 'apps/api/src/portable-bundle.ts').read_text()
        self.assertIn('slide_asset_id', bundle)

    def test_worker_has_isolated_pdf_export(self):
        worker = (ROOT / 'tools/conversion_worker.py').read_text()
        self.assertIn('portable-export-pdf', worker)
        self.assertIn('export-pdf', worker)

    def test_invalid_or_non_slide_snapshot_is_rejected(self):
        for item in [
            {'type':'slide', 'slide_asset_id':'../../file'},
            {'type':'poll', 'slide_asset_id':str(uuid.uuid4())},
        ]:
            with self.subTest(item=item):
                with self.assertRaisesRegex(ValueError, 'slide|Slide'):
                    _validate_export_input({'format':'quorivio-session','version':1,
                        'activities':[{**item,'page_design':{'widgets':[]}}]})



class RC200NativePowerPointPortability(unittest.TestCase):
    """Needs python-pptx and Pillow; run only after CI installs conversion dependencies."""
    def test_raster_snapshot_round_trip_to_editable_pptx(self):
        from PIL import Image
        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        with tempfile.TemporaryDirectory() as folder:
            media = Path(folder)
            uid = str(uuid.uuid4())
            png = io.BytesIO()
            Image.new('RGB', (32, 18), (18, 57, 145)).save(png, format='PNG')
            raw = png.getvalue()
            (media / uid).write_bytes(raw)
            definition = {'format':'quorivio-session', 'version':1,
                'session':{'theme':{}},'activities':[{'type':'slide','slide_asset_id':uid,
                    'page_design':{'widgets':[{'id':'caption','kind':'text','label':'Didascalia',
                        'position':{'x':10,'y':5,'width':70,'height':20}}]}}]}
            dest = media / 'out.pptx'
            portable_to_pptx(definition, dest, media_dir=media)
            slide = Presentation(dest).slides[0]
            self.assertEqual(slide.shapes[0].shape_type, MSO_SHAPE_TYPE.PICTURE)
            self.assertEqual(slide.shapes[0].image.blob, raw)
            self.assertEqual(slide.shapes[0].width, Presentation(dest).slide_width)
            self.assertEqual(slide.shapes[0].height, Presentation(dest).slide_height)
            self.assertEqual(slide.shapes[1].text, 'Didascalia')

    def test_missing_snapshot_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            data={'format':'quorivio-session','version':1,
                'activities':[{'type':'slide','slide_asset_id':str(uuid.uuid4()),
                    'page_design':{'widgets':[]}}]}
            with self.assertRaisesRegex(ValueError, 'Missing or oversized'):
                portable_to_pptx(data, Path(folder)/'out.pptx', media_dir=folder)


if __name__ == '__main__': unittest.main()
