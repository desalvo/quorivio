"""Run real Poppler + LibreOffice against isolated /tmp and /conversions devices.

After installing native conversion dependencies in GitHub Actions, reproduce
Kubernetes's two-emptyDir topology using /dev/shm as the conversion workspace
and /tmp as the system temporary directory. The pre-RC261 rename fails EXDEV.
"""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from tools.import_presentation import convert


class NativeSeparateMountAcceptance(unittest.TestCase):
    def test_pdf_image_import_publishes_atomically_across_mount_boundary(self):
        from reportlab.pdfgen.canvas import Canvas
        with self._kube_layout() as workspace:
            workspace=Path(workspace)
            pdf=workspace/'source.pdf'
            doc=Canvas(str(pdf),pagesize=(400,250))
            doc.drawString(25,200,'Quorivio RC261 PDF flattened image conversion')
            doc.showPage()
            doc.save()
            result=convert(pdf,workspace/'pages')
            self._assert_complete(workspace,result,'pdf')

    def test_pptx_image_import_publishes_atomically_across_mount_boundary(self):
        from pptx import Presentation
        from pptx.util import Inches
        with self._kube_layout() as workspace:
            workspace=Path(workspace)
            deck=Presentation()
            slide=deck.slides.add_slide(deck.slide_layouts[6])
            slide.shapes.add_textbox(Inches(1),Inches(1),Inches(4),Inches(1)).text='RC261 PPTX'
            source=workspace/'source.pptx'
            deck.save(source)
            result=convert(source,workspace/'pages')
            self._assert_complete(workspace,result,'pptx')

    def _kube_layout(self):
        if not Path('/dev/shm').is_dir():
            self.skipTest('Linux shared-memory filesystem unavailable')
        if os.stat('/dev/shm').st_dev==os.stat(tempfile.gettempdir()).st_dev:
            self.skipTest('system temporary directory and /dev/shm share a device')
        return tempfile.TemporaryDirectory(prefix='quorivio-native-rc261-',dir='/dev/shm')

    def _assert_complete(self, temp, result, source_type):
        workspace=Path(temp)
        self.assertEqual(result['page_count'],1)
        self.assertEqual(result['source_type'],source_type)
        self.assertEqual(len(result['pages']),1)
        page=result['pages'][0]
        self.assertEqual(page['image'],'page-0001.png')
        contents=(workspace/'pages'/page['image']).read_bytes()
        self.assertEqual(page['sha256'],hashlib.sha256(contents).hexdigest())
        self.assertEqual(page['bytes'],len(contents))
        self.assertTrue((workspace/'pages'/'manifest.json').is_file())
        self.assertFalse(list(workspace.glob('.quorivio-import-*')))

if __name__=='__main__':unittest.main()
