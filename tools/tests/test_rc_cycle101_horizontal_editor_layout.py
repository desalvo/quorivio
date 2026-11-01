"""RC101: horizontal widget palette must not push slide outside the viewport."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf-8')
TEST = (ROOT / 'tools/ci_editor_mock_layout_chromium.py').read_text(encoding='utf-8')
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')


class HorizontalEditorGridRegression(unittest.TestCase):
    def test_fixed_middle_row_and_remaining_slide_height(self):
        self.assertRegex(CSS, r'grid-template-rows:78px 80px minmax\(0,1fr\)!important')
        self.assertRegex(CSS, r'grid-template-rows:64px 80px minmax\(0,1fr\)!important')
        self.assertIn('height:80px!important;max-height:80px!important', CSS)
        self.assertIn('height:80px!important;max-height:80px!important;', CSS)

    def test_browser_acceptance_checks_real_current_layout(self):
        self.assertIn('name="viewport"', TEST)
        self.assertIn("rb['y']+rb['height']<=sb['y']+3", TEST)
        self.assertIn("cb['y']+cb['height']<=sb['y']+sb['height']+1", TEST)
        self.assertIn("overflow['scrollWidth']>overflow['clientWidth']+100", TEST)
        self.assertNotIn("sb['x']+sb['width']<=rb['x']+5", TEST)

    def test_browser_step_remains_mandatory_in_opt_in_campaign(self):
        self.assertIn('python3 tools/ci_editor_mock_layout_chromium.py', CI)
        self.assertIn('python3 -m unittest tools.tests.test_rc_cycle101_horizontal_editor_layout -q', CI)


if __name__ == '__main__':
    unittest.main()
