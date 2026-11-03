"""Early CI guard for RC155: revision conflict must not be hidden by floating ribbon."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT.joinpath('apps/web/src/main.tsx').read_text(encoding='utf8')
TEST=ROOT.joinpath('apps/web/test/rc139-rating-editor-selection.test.ts').read_text(encoding='utf8')


def valid(text: str) -> bool:
    return ("active&&!ribbonDismissed&&!suspendFormattingRibbon&&widgets.some" in text
            and "suspendFormattingRibbon={pageConflict}" in text
            and "onClick={()=>setRibbonDismissed(true)}" in text
            and "onClick={()=>void inspectPageConflict()}" in text)


class RC155ConflictRibbon(unittest.TestCase):
    def test_revision_conflict_suspends_ribbon_but_retains_selection(self):
        self.assertTrue(valid(SOURCE))
        self.assertIn('!suspendFormattingRibbon', TEST)
        self.assertIn('suspendFormattingRibbon=', TEST)

    def test_missing_ribbon_suspension_fails_closed(self):
        mutated=SOURCE.replace('!suspendFormattingRibbon&&', '', 1)
        self.assertNotEqual(mutated,SOURCE)
        self.assertFalse(valid(mutated))

    def test_missing_conflict_wiring_fails_closed(self):
        mutated=SOURCE.replace('suspendFormattingRibbon={pageConflict}', 'suspendFormattingRibbon={false}', 1)
        self.assertNotEqual(mutated,SOURCE)
        self.assertFalse(valid(mutated))

    def test_clearing_selection_on_close_fails_closed(self):
        mutated=SOURCE.replace('onClick={()=>setRibbonDismissed(true)}', 'onClick={()=>{setActive(null);setRibbonDismissed(true)}}', 1)
        self.assertNotEqual(mutated,SOURCE)
        self.assertFalse(valid(mutated))


if __name__=='__main__':
    unittest.main()
