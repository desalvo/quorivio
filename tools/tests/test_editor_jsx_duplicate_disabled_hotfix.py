"""Regression for CI 40209267607 / TS17001 in the editor conflict button."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class EditorJsxDuplicateDisabledHotfix(unittest.TestCase):
    def test_conflict_inspect_button_combines_disabled_conditions(self):
        source = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf-8')
        marker = 'onClick={()=>void inspectPageConflict()}'
        self.assertEqual(source.count(marker), 1)
        start = source.rfind('<button', 0, source.index(marker))
        end = source.index('>', source.index(marker))
        opening_tag = source[start:end]
        self.assertEqual(opening_tag.count('disabled='), 1)
        self.assertIn('disabled={pageSavePending || !!mergeCandidate?.local}', opening_tag)


if __name__ == '__main__':
    unittest.main()
