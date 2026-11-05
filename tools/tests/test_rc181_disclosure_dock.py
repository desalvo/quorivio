"""RC181: preflight must assert the corrected disclosure geometry, not the old defect."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class AccessibleDockRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = (ROOT / 'tools/ci_accessible_disclosure_chromium.py').read_text(encoding='utf8')
        cls.workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
        cls.css = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')
        cls.legacy = (ROOT / 'tools/tests/test_ci_mobile_disclosure_overlap.py').read_text(encoding='utf8')

    def test_real_css_and_current_non_overlapping_dock_are_required(self):
        self.assertIn('apps/web/src/style.css', self.browser)
        self.assertIn("assert not overlap", self.browser)
        self.assertNotIn("assert overlap, 'Fixture must intentionally reproduce", self.browser)
        self.assertIn('position:relative!important', self.css.split('/* RC180', 1)[1])
        self.assertIn('assert not overlap', self.legacy)

    def test_disclosure_and_toolbar_remain_operable_with_native_pointers(self):
        self.assertIn('elementFromPoint', self.browser)
        self.assertIn('await check.check()', self.browser)
        self.assertIn("await expect(group).to_be_hidden()", self.browser)
        self.assertIn("await expect(page.locator('#result')).to_have_text('edited')", self.browser)
        self.assertIn('await (summary.tap() if touch else summary.click())', self.browser)
        self.assertIn('await verify(browser,390,844,True)', self.browser)
        self.assertIn('await verify(browser,1440,1000,False)', self.browser)
        self.assertNotIn('force=True', self.browser)
        self.assertNotIn('dispatch_event(', self.browser)

    def test_fail_fast_before_full_chromium_suite_and_preserve_older_receipts(self):
        early='python3 -m unittest tools.tests.test_rc181_disclosure_dock -q'
        self.assertIn(early, self.workflow)
        self.assertLess(self.workflow.index(early), self.workflow.index('python3 tools/ci_accessible_disclosure_chromium.py'))
        self.assertIn('python3 tools/verify_rc_cycle180_inventory.py --historical',self.workflow)
        self.assertIn('python3 tools/verify_rc_cycle181_inventory.py',self.workflow)

if __name__ == '__main__':
    unittest.main()
