from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()

class ShapePaintUIContracts(unittest.TestCase):
    def test_canvas_has_editable_shape_paint_inspector(self):
        self.assertIn('aria-label="Stile forma PowerPoint"',MAIN)
        self.assertIn('{shapePaintEditor}',MAIN)
    def test_editor_exposes_all_native_line_properties(self):
        for text in ('Spessore contorno','Tratteggio contorno','Nessun contorno','Nessun riempimento'):
            self.assertIn(text,MAIN)
    def test_presenter_and_rehearsal_share_dash_and_no_fill(self):
        self.assertGreaterEqual(MAIN.count("style?.strokeDash==='dot'"),2)
        self.assertIn("backgroundColor:w.style?.fillNone?'transparent'",MAIN)
    def test_page_thumbnails_do_not_force_opaque_fill(self):
        self.assertIn("backgroundColor:w.style?.fillNone?'transparent':w.style?.fillColor",MAIN)
    def test_server_persists_and_bounds_shape_paint(self):
        for token in ('strokeWidth?:number',"strokeDash?:'solid'|'dash'|'dot'",'v.strokeWidth<=12',"['fillNone','strokeNone']"):
            self.assertIn(token,DOMAIN)
