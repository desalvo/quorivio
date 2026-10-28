from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MAIN = (ROOT/'apps/web/src/main.tsx').read_text()
CSS = (ROOT/'apps/web/src/style.css').read_text()

class PictureCropUIContracts(unittest.TestCase):
    def test_projection_uses_crop_aware_media(self):
        self.assertIn('<CroppedImage className="projection-media"', MAIN)
        self.assertIn('crop={widget.crop}', MAIN)
    def test_preview_uses_same_crop_aware_media(self):
        self.assertIn('<ProjectionWidgetContent sessionId={snapshot.session.id} widget={w} activity={a}/>',MAIN)
        self.assertIn('<CroppedImage className="projection-media"',MAIN)
        self.assertIn('crop={widget.crop}',MAIN)
    def test_editor_has_four_sided_crop_controls(self):
        self.assertIn("(['left','right','top','bottom'] as const)", MAIN)
        self.assertIn('Ritaglio immagine PowerPoint', MAIN)
    def test_editor_can_restore_full_image(self):
        self.assertIn('crop:undefined', MAIN)
    def test_crop_is_clipped_and_not_a_css_injection(self):
        self.assertIn('overflow:hidden', CSS)
        self.assertIn("Number.isFinite(v)", MAIN)
        self.assertIn('l+r>=0.99||t+b>=0.99', MAIN)
    def test_accessibility_and_mobile_inputs(self):
        self.assertIn('role="img" aria-label={alt}', MAIN)
        self.assertIn('min-height:44px', CSS)
