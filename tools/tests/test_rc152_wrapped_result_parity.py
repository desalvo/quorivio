"""RC152 browser regression for the RC143 wrapping rule across 4 surfaces.

Exercises real production CSS in Chromium with synthetic results only. Mutation
probes must be rejected: an all-nowrap label or detached count is a regression.
"""
import unittest
from pathlib import Path
from tools import ci_rc141_widget_parity_chromium as parity

ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')


class RC152WrappedResultParity(unittest.TestCase):
    def test_current_results_use_last_word_and_count_group(self):
        self.assertIn('className="linked-result-pair"', UI)
        self.assertIn('className="linked-result-final"', UI)
        self.assertIn('splitResultLabel(r.label).prefix', UI)
        self.assertIn('splitResultLabel(r.label).last', UI)
        self.assertIn('chart===\'cloud\'?`[${r.count}]`', UI)
        self.assertIn('--authored-widget-font-size:16px', parity.markup('participant'))

    def test_real_chromium_wraps_and_preserves_count_on_all_surfaces(self):
        parity.run()

    def test_regression_entire_label_forced_no_wrap_is_rejected(self):
        broken = parity.CSS + '\n.linked-results .linked-results-row .linked-result-pair{white-space:nowrap!important}\n'
        with self.assertRaises(AssertionError):
            parity.run(broken)

    def test_regression_detached_last_word_and_count_is_rejected(self):
        broken = parity.CSS + '\n.linked-results .linked-results-row .linked-result-pair>.linked-result-final{white-space:normal!important}\n'
        with self.assertRaises(AssertionError):
            parity.run(broken)


if __name__ == '__main__':
    unittest.main()
