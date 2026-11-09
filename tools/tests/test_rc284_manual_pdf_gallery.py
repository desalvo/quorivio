"""RC284: real screenshot PDFs must contain images, not literal HTML figures."""
from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from manual_screenshot_catalog import CATALOG, SCREENSHOTS, HISTORIC_SCREENSHOTS, evidence, gallery


class RC284ManualPDFGallery(unittest.TestCase):
    def test_verified_historic_evidence_is_preserved(self):
        data=evidence(HISTORIC_SCREENSHOTS,
            expected_commit='0bb89e6ac79ed57493130f06fc5042182a166ed6',minimum=13)
        self.assertEqual(len(data['shots']),13)
        self.assertEqual(data['fixture'],'synthetic-only')
        # Local PDFs may include these images only with the original build id.
        content=gallery('admin','it',path=HISTORIC_SCREENSHOTS)
        self.assertNotIn('Commit ',content)
        self.assertIn('ARCHIVIO RC283',content)
        self.assertNotIn('CURRENT BUILD',content)

    def test_historical_screenshots_cannot_satisfy_current_ci_capture(self):
        with self.assertRaises(ValueError):
            gallery('user','it',path=HISTORIC_SCREENSHOTS,require=True,commit='f'*40)
        with self.assertRaises(ValueError):
            gallery('user','it',path=HISTORIC_SCREENSHOTS,require=True,
                    commit='0bb89e6ac79ed57493130f06fc5042182a166ed6')
        # The generation workflow still uses --require-real, never a fallback.
        self.assertIn('generate_manuals.py --require-real',
                      (ROOT/'.github/workflows/ci.yml').read_text())

    def test_published_pdf_has_large_images_next_to_real_captions(self):
        root=Path(os.environ.get('QUORIVIO_MANUAL_OUTPUT_DIR',str(ROOT/'docs/manuals')))
        shotroot=SCREENSHOTS if (SCREENSHOTS/'capture.json').is_file() else HISTORIC_SCREENSHOTS
        data=evidence(shotroot,minimum=9)
        for role in ('user','presenter','admin'):
            expected=sum(role in CATALOG[stem] for stem in data['shots'])
            for lang in ('it','en'):
                with self.subTest(role=role,lang=lang):
                    path=root/f'{role}-guide.{lang}.pdf'
                    doc=fitz.open(path)
                    label='SCHERMATA REALE' if lang=='it' else 'REAL APP SCREENSHOT'
                    text='\n'.join(p.get_text() for p in doc)
                    self.assertEqual(text.count(label),expected)
                    self.assertNotIn('<figure',text)
                    self.assertNotIn('<img src=',text)
                    for page in doc:
                        if label in page.get_text():
                            self.assertTrue(any(
                                im['bbox'][2]-im['bbox'][0]>160 and
                                im['bbox'][3]-im['bbox'][1]>110
                                for im in page.get_image_info()),
                                'Genuine screenshot caption without visible PDF image')
                    doc.close()


if __name__ == '__main__':
    unittest.main()
