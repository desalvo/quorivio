"""RC173 fail-closed public slide source and inventory contracts."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RC173PublicStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
        cls.css = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')
        cls.policy = (ROOT / 'apps/web/src/live-slide-policy.ts').read_text(encoding='utf8')
        start = cls.ui.index('{joinPath?<main id="main-content"')
        end = cls.ui.index('publicPath?<PresenterLiveScreen', start)
        cls.participant = cls.ui[start:end]

    def test_wrapper_is_not_second_slide_background(self):
        self.assertIn('style={{backgroundColor:"transparent",backgroundImage:"none"}}', self.participant)
        self.assertIn('...slideBackgroundCss(entry.activity.page_design', self.participant)
        self.assertNotIn('participant-live-view" style={window.matchMedia', self.participant)

    def test_reading_and_fidelity_are_explicit_separate_modes(self):
        self.assertIn('const audiencePortrait=joinPath&&participantPhoneMode&&!participantReadingMode', self.ui)
        for label in ('Diapositiva 16:9', 'Layout smartphone', 'Lettura accessibile'):
            self.assertIn(label, self.participant)
        self.assertIn('stage-reading{\n  background:#fff!important;background-image:none!important', self.css)
        self.assertIn('stage-fidelity :is(button,select,input,textarea){', self.css)

    def test_private_results_background_is_filtered_before_mobile_layout(self):
        self.assertIn('isOrphanResultFill', self.policy)
        self.assertIn('const visible = participantVisibleWidgets(widgets);', self.policy)
        self.assertNotIn('<h3>Risultati live</h3>', self.participant)

    def test_editor_does_not_duplicate_rating_title(self):
        self.assertIn("!(w.kind==='rating'&&editing!==w.id)", self.ui)
        self.assertIn("w.kind==='rating'?{...w,showTitle:editing===w.id?false:w.showTitle}", self.ui)


if __name__ == '__main__':
    unittest.main()
