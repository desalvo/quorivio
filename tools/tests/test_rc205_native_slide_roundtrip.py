"""Run only AFTER python-pptx and Pillow are installed (late CI step)."""
from __future__ import annotations

import io
from pathlib import Path
import sys
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from pptx_portable import portable_to_pptx


class RC205NativeSlideRoundTrip(unittest.TestCase):
    def test_imported_slide_image_widget_does_not_duplicate_snapshot(self):
        from PIL import Image
        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            uid = str(uuid.uuid4())
            buffer = io.BytesIO()
            Image.new('RGB', (64, 36), (34, 89, 162)).save(buffer, format='PNG')
            raw = buffer.getvalue()
            (folder / uid).write_bytes(raw)
            data = {'format': 'quorivio-session', 'version': 1, 'session': {'theme': {}},
                    'activities': [{'type': 'slide', 'slide_asset_id': uid, 'page_design': {
                        'widgets': [{'id': 'imported_slide', 'kind': 'image', 'label': 'Slide 1',
                                     'assetId': uid, 'position': {'x': 0, 'y': 0, 'width': 100,
                                                                   'height': 100, 'rotation': 0}}]}}]}
            result = folder / 'result.pptx'
            portable_to_pptx(data, result, media_dir=folder)
            shapes = Presentation(result).slides[0].shapes
            self.assertEqual(len(shapes), 1)
            self.assertEqual(shapes[0].shape_type, MSO_SHAPE_TYPE.PICTURE)
            self.assertEqual(shapes[0].image.blob, raw)

    def test_non_snapshot_overlay_remains_editable(self):
        from PIL import Image
        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            slide_asset=str(uuid.uuid4());overlay_asset=str(uuid.uuid4())
            for name, color in ((slide_asset,(44,77,180)),(overlay_asset,(128,25,50))):
                image=io.BytesIO();Image.new('RGB',(16,9),color).save(image,format='PNG')
                (folder/name).write_bytes(image.getvalue())
            data={'format':'quorivio-session','version':1,'session':{'theme':{}},
                  'activities':[{'type':'slide','slide_asset_id':slide_asset,
                  'page_design':{'widgets':[{'id':'overlay','kind':'image', 'assetId':overlay_asset,
                  'position':{'x':20,'y':20,'width':30,'height':30,'rotation':0}}]}}]}
            dest=folder/'two.pptx';portable_to_pptx(data,dest,media_dir=folder)
            shapes=Presentation(dest).slides[0].shapes
            self.assertEqual(len(shapes),2)
            self.assertTrue(all(s.shape_type==MSO_SHAPE_TYPE.PICTURE for s in shapes))

if __name__=='__main__':
    unittest.main()
