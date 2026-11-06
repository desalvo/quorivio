"""RC222 pre-npm guard for compact widget typography and editor-only option wrapping."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
RICH=(ROOT/'apps/web/src/widget-text-marks.ts').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def guard(ui=UI,css=CSS,rich=RICH):
    expected_ui=[
        'style={answerOptionStyle(widgetTextDefaults(w.kind,w.style))} aria-label="Opzioni di risposta del widget"',
        'className="canvas-subquestion-option" style={answerOptionStyle(widgetTextDefaults(w.kind,w.style))}',
        "const activeTextField=effectiveScope==='widget'?null:",
        'patch(w.id,applyAllWidgetTypeface(w,changes as InlineStyle))',
        '<details className="palette-ribbon-advanced"><summary>Testi indipendenti…</summary>',
        "role=\"tabpanel\" tabIndex={0} aria-label={'Opzioni '+formatTab}",
    ]
    expected_css=[
        'display:inline!important;align-items:baseline!important;white-space:inherit!important;',
        'body .editor-floating-panel.widget-selection-palette .palette-ribbon-group-title{',
        'max-height:calc(100dvh - 55px)!important;',
        'flex-wrap:nowrap!important;justify-content:flex-start!important;',
        '.canvas-subquestion-option>.widget-rich-inline>span',
        '--q-answer-font-family,Arial',
    ]
    for needle in expected_ui:
        if needle not in ui:raise AssertionError('editor source contract: '+needle)
    for needle in expected_css:
        if needle not in css:raise AssertionError('editor stylesheet contract: '+needle)
    if 'answerFontFamily:change.fontFamily' not in rich:
        raise AssertionError('answer-wide font persistence missing')


class RC222CompactWidgetFormat(unittest.TestCase):
    def test_editor_defaults_wrap_and_full_widget_updates(self):guard()

    def test_negative_missing_answer_font(self):
        with self.assertRaisesRegex(AssertionError,'source contract'):
            guard(ui=UI.replace('style={answerOptionStyle(widgetTextDefaults(w.kind,w.style))} aria-label="Opzioni di risposta del widget"',
                                'style={answerOptionStyle(w.style)} aria-label="Opzioni di risposta del widget"',1))

    def test_negative_missing_rich_glyph_wrapping(self):
        with self.assertRaisesRegex(AssertionError,'stylesheet contract'):
            guard(css=CSS.replace('display:inline!important;align-items:baseline!important;white-space:inherit!important;',
                                  'display:flex!important;white-space:nowrap!important;',1))

    def test_negative_missing_whole_widget_font(self):
        with self.assertRaisesRegex(AssertionError,'answer-wide font persistence'):
            guard(rich=RICH.replace('answerFontFamily:change.fontFamily','answerFontFamily:undefined',1))

    def test_preflight_runs_before_npm_and_chromium_acceptance(self):
        self.assertIn('tools.tests.test_rc222_compact_editor_answers',CI)
        self.assertLess(CI.index('tools.tests.test_rc222_compact_editor_answers'),CI.index('Install reproducibly'))
        self.assertIn('tools/ci_rc222_format_widget_chromium.py',CI)

if __name__=='__main__':unittest.main()
