"""RC198 source contracts for answer styles and cumulative CI inventory continuity."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

def source(path: str) -> str:
    return (ROOT/path).read_text(encoding='utf-8')

class AnswerDecorationContract(unittest.TestCase):
    def test_api_rejects_invalid_answer_decoration_values(self):
        schema = source('apps/api/src/domain.ts')
        for name in ('answerUnderline', 'answerStrikethrough'):
            self.assertIn(f'{name}?:boolean', schema)
            self.assertIn(f"'{name}'", schema)
        self.assertIn("'answerUnderline','answerStrikethrough'].every", schema)

    def test_view_preserves_both_independent_answer_decorations(self):
        answer = source('apps/web/src/widget-answer-style.ts')
        self.assertIn("style?.answerUnderline?'underline'", answer)
        self.assertIn("style?.answerStrikethrough?'line-through'", answer)
        marks = source('apps/web/src/widget-text-marks.ts')
        self.assertIn('answerUnderline:change.underline', marks)
        self.assertIn('answerStrikethrough:change.strikethrough', marks)
        main = source('apps/web/src/main.tsx')
        self.assertIn("underline:'answerUnderline',strikethrough:'answerStrikethrough'", main)
        self.assertIn('aria-label="Sottolineato risposte"', main)
        self.assertIn('aria-label="Barrato risposte"', main)

    def test_rc197_is_historical_and_rc198_is_current_inventory(self):
        workflow=source('.github/workflows/ci.yml')
        self.assertIn('python3 tools/verify_rc_cycle197_inventory.py --historical',workflow)
        self.assertIn('python3 tools/verify_rc_cycle198_inventory.py',workflow)
        self.assertLess(workflow.index('python3 tools/verify_rc_cycle197_inventory.py --historical'),workflow.index('python3 tools/verify_rc_cycle198_inventory.py'))
        self.assertIn("MANIFEST = 'docs/validation/RC_CYCLE198_PACKAGE_INVENTORY_20261105.json'",source('tools/verify_rc_cycle198_inventory.py'))

if __name__ == '__main__':
    unittest.main()
