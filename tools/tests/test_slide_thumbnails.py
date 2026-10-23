"""Static regression: actual slide previews and non-pointer reordering."""
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]

class SlideThumbnailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui=(ROOT/'apps/web/src/main.tsx').read_text()
        cls.css=(ROOT/'apps/web/src/style.css').read_text()

    def test_thumbnails_use_persisted_widget_layout(self):
        self.assertIn('miniature-slide', self.ui)
        self.assertIn('page_design?.widgets||[]', self.ui)
        self.assertIn('w.position?.rotation||0', self.ui)
        self.assertIn('miniature-widget', self.css)

    def test_keyboard_reordering_is_gated_and_uses_same_endpoint(self):
        self.assertIn("!e.altKey||snap.session.status==='closed'", self.ui)
        self.assertIn("e.key==='ArrowLeft'", self.ui)
        self.assertIn("e.key==='ArrowRight'", self.ui)
        self.assertIn('void dropPage(a.id,snap.activities[i-1].id)', self.ui)
        self.assertIn('void dropPage(a.id,snap.activities[i+1].id)', self.ui)

if __name__=='__main__':unittest.main()
