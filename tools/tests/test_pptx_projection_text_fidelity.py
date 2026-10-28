"""Guard the live projection against regressions in imported text fidelity."""
import unittest
from pathlib import Path

WEB = (Path(__file__).resolve().parents[2] / 'apps/web/src/main.tsx').read_text()

class ProjectionTextFidelity(unittest.TestCase):
    def test_full_imported_description_not_rendered_twice(self):
        self.assertIn("widget.description?.startsWith(widget.label||'')", WEB)
        self.assertIn("whiteSpace:'pre-wrap'", WEB)

    def test_pptx_text_style_is_applied_on_presenter_projection(self):
        self.assertIn("const textStyle={fontFamily:widget.style?.fontFamily", WEB)
        self.assertIn("{...textStyle,textAlign:widget.style?.textAlign", WEB)

    def test_audience_renders_full_editable_text_without_duplication(self):
        self.assertIn("w.kind==='text'?<p style={{whiteSpace:'pre-wrap'", WEB)
        self.assertIn("w.kind==='postit'?<div className=\"rehearsal-postit\" style=", WEB)

    def test_rehearsal_uses_imported_typography_and_full_text(self):
        self.assertIn("...widgetTypographyStyle(w.style)", WEB)
        self.assertIn('<ProjectionWidgetContent sessionId={snapshot.session.id} widget={w} activity={activity}/>', WEB)

if __name__ == '__main__': unittest.main()
