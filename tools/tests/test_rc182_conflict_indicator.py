"""RC182: fail-fast, mutation-resistant conflict-status geometry regression."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


class RC182ConflictIndicator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
        cls.workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        cls.browser=(ROOT/'tools/ci_browser_editor_conflict_visibility.py').read_text(encoding='utf8')

    def test_error_status_can_wrap_without_rc171_hard_width(self):
        # The original 140px important cap remains correct for success status,
        # but cannot apply to conflict/error status. Assert a subsequent
        # more-specific override and wrap policy (not a fixed pixel workaround).
        self.assertIn('.editor-ux-v2 .editor-autosave-indicator{max-width:140px!important;min-width:100px!important}',self.css)
        latest=self.css.split('/* RC182:',1)[1]
        self.assertRegex(latest,r'\.editor-ux-v2 \.editor-autosave-indicator\.has-error\s*\{')
        self.assertIn('max-width:min(28rem,calc(100vw - 24px))!important',latest)
        self.assertIn('min-width:0!important',latest)
        self.assertIn('white-space:normal!important',latest)
        self.assertIn('overflow-wrap:anywhere',latest)
        self.assertIn('overflow:visible!important',latest)

    def test_chromium_stresses_font_metrics_and_long_messages(self):
        self.assertIn('for width in (1440, 1100, 960, 390)',self.browser)
        self.assertIn('e.style.fontSize=\'14px\'',self.browser)
        self.assertIn('Impossibile salvare: conflitto di revisione',self.browser)
        self.assertIn("values['scroll'] <= values['w'] + 3",self.browser)
        self.assertNotIn('force=True',self.browser)

    def test_browser_runs_before_its_postgres_integration_duplicate(self):
        pre='python3 -m unittest tools.tests.test_rc182_conflict_indicator -q'
        script='python3 tools/ci_browser_editor_conflict_visibility.py'
        self.assertIn(pre,self.workflow)
        self.assertEqual(self.workflow.count(script),2)
        self.assertLess(self.workflow.index(pre),self.workflow.index(script))
        self.assertLess(self.workflow.index(script),self.workflow.index('python3 tools/ci_browser_editor_postgres.py'))
        self.assertIn('python3 tools/verify_rc_cycle181_inventory.py --historical',self.workflow)

if __name__=='__main__':
    unittest.main()
