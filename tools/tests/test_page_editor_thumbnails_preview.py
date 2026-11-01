"""Structural regression checks for in-editor page thumbnails and unsaved draft safety."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class PageEditorThumbnailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tsx = (ROOT/'apps/web/src/main.tsx').read_text()
        cls.css = (ROOT/'apps/web/src/style.css').read_text()

    def test_thumbnail_renders_saved_widget_geometry(self):
        self.assertIn('page-editor-preview-widget', self.tsx)
        self.assertIn('page_design?.widgets||[]', self.tsx)
        self.assertIn('page-editor-preview-widget{position:absolute', self.css)

    def test_reordering_checks_unsaved_changes(self):
        self.assertIn("sourceId===targetId||!confirmPageNavigation()", self.tsx)
        self.assertIn("snap.session.status==='closed'||!confirmPageNavigation()", self.tsx)

    def test_dashboard_return_respects_unsaved_changes(self):
        self.assertIn("if(confirmPageNavigation())setDesignActivity('')", self.tsx)

if __name__=='__main__': unittest.main()
