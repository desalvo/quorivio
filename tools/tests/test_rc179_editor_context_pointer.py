"""RC179: contextual editor commands must outrank the wrapped insertion rail."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
BROWSER = (ROOT / 'tools/ci_rc179_editor_tool_pointer_chromium.py').read_text(encoding='utf8')


class ContextualPointerAcceptance(unittest.TestCase):
    def test_stage_stacking_context_rises_only_when_tools_open(self):
        # A child z-index alone is insufficient: it cannot escape the parent
        # stage's lower stacking context. The menu should not permanently mask
        # the palette while closed.
        rule = re.search(
            r'\.editor-ux-v2\s+\.editor-stage:has\(\.canvas-editor-group\[data-tools-open="true"\]\)\s*\{([^}]+)\}',
            CSS,
        )
        self.assertIsNotNone(rule)
        self.assertIn('z-index:70!important', rule.group(1))
        self.assertIn('z-index:13', CSS)  # Rail remains interactive normally.

    def test_native_chromium_regression_is_executed_before_editor_e2e(self):
        self.assertIn('python3 tools/ci_rc179_editor_tool_pointer_chromium.py', CI)
        self.assertLess(CI.index('python3 tools/ci_rc179_editor_tool_pointer_chromium.py'),
                        CI.index('python3 tools/ci_browser_editor.py'))
        self.assertIn('tools.tests.test_rc179_editor_context_pointer', CI)
        self.assertIn('document.elementFromPoint(x,y)', BROWSER)
        self.assertIn('await button.click(timeout=3000)', BROWSER)
        self.assertIn('QUORIVIO_CHROMIUM_PATH', BROWSER)
        self.assertIn('for width, height in [(1440, 900), (960, 800), (390, 844)]', BROWSER)
        self.assertNotIn('force=True', BROWSER)
        self.assertNotIn('dispatch_event(', BROWSER)

    def test_legacy_css_without_rc179_rule_cannot_satisfy_contract(self):
        legacy = CSS.split('/* RC179: the wrapped insertion palette', 1)[0]
        self.assertNotIn('.editor-stage:has(.canvas-editor-group[data-tools-open="true"])', legacy)


if __name__ == '__main__':
    unittest.main()
