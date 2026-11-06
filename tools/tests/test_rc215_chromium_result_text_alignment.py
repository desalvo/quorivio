"""RC215: measure real glyph alignment instead of mixing range and box top.

RC214 full CI 42144060435 failed RC141 at the word/count alignment
assertion despite both glyph ranges sharing exactly the same baseline.
Keep the test's wrapping, bounds and four-surface assertions intact.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
BROWSER=(ROOT/'tools/ci_rc141_widget_parity_chromium.py').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def verify_word_count_glyph_alignment(source:str):
    for expected in (
        'const finalWord=document.createRange();finalWord.selectNodeContents(final.firstChild);',
        'const countText=document.createRange();countText.selectNodeContents(count);',
        'const wordRect=finalWord.getBoundingClientRect();',
        'const countRect=countText.getBoundingClientRect();',
        'Math.abs(wordRect.top-countRect.top)<1.5',
        'countRect.left>wordRect.right',
        'countRect.left-wordRect.right<28',
        "item['pairWraps'] and item['labelWraps'] and item['tailInline'] and item['tailNoWrap'] and item['pairFits']",
        "for viewport in (1440, 390):",
        "('editor','presenter','rehearsal','participant')",
    ):
        if expected not in source:
            raise AssertionError('missing glyph alignment or four-surface contract: '+expected)
    if 'finalWord.getBoundingClientRect().top-count.getBoundingClientRect().top' in source:
        raise AssertionError('mixed glyph and element box coordinates must not be compared')


class RC215GlyphAlignment(unittest.TestCase):
    def test_true_glyph_rects_and_full_parity(self):
        verify_word_count_glyph_alignment(BROWSER)
        self.assertIn('tools.tests.test_rc215_chromium_result_text_alignment',WORKFLOW)
        self.assertIn('python3 tools/ci_rc141_widget_parity_chromium.py',WORKFLOW)

    def test_invalid_mutations_fail_closed(self):
        for original,mutation in (
            ('countText.selectNodeContents(count)', 'countText.selectNodeContents(final)'),
            ('wordRect.top-countRect.top', 'wordRect.top-count.getBoundingClientRect().top'),
            ('countRect.left>wordRect.right', 'countRect.left<wordRect.right'),
            ('countRect.left-wordRect.right<28', 'countRect.left-wordRect.right<500'),
            ("item['labelWraps']", 'true'),
            ("for viewport in (1440, 390):", "for viewport in (1440,):"),
        ):
            self.assertIn(original,BROWSER)
            with self.assertRaises(AssertionError):
                verify_word_count_glyph_alignment(BROWSER.replace(original,mutation,1))

if __name__=='__main__':unittest.main()
