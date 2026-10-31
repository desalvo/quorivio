"""RC78: real-browser rehearsal button locators follow accessible names, not legacy icon glyphs."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RC78PreviewSelector(unittest.TestCase):
    def test_browser_clicks_current_accessible_button_not_obsolete_glyph(self):
        script = (ROOT / 'tools/ci_rehearsal_singleton_offline_chromium.py').read_text(encoding='utf8')
        self.assertIn("preview_group=page.get_by_role('group',name='Anteprime della sessione')", script)
        self.assertIn("dashboard_open=preview_group.get_by_role('button',name='Anteprime affiancate',exact=True)", script)
        self.assertNotIn("name='▣ Anteprime affiancate'", script)
        self.assertIn('await expect(dashboard_open).to_have_count(1)', script)
        self.assertIn('await expect(dashboard_open).to_be_visible()', script)
        self.assertIn('await dashboard_open.click()', script)
        self.assertIn("dashboard_overlay=page.locator('.rehearsal-backdrop')", script)
        self.assertIn('assert await dashboard_open.evaluate', script)

    def test_app_really_renders_the_accessible_button_in_draft_dashboard(self):
        ui = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
        self.assertIn('role="group" aria-label={snap.session.status', ui)
        self.assertIn("'Anteprime della sessione'", ui)
        self.assertIn("<Square size={22}/> Anteprime affiancate", ui)
        self.assertIn("onClick={()=>{setRehearsalMode(m);setRehearsalOpen(true)}}", ui)
        self.assertIn('rehearsalOpen&&!designActivity', ui)

    def test_both_real_browser_engines_keep_the_same_rehearsal_preflight(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('python3 tools/ci_rehearsal_singleton_offline_chromium.py\n', workflow)
        self.assertIn('python3 tools/ci_rehearsal_singleton_offline_chromium.py --engines firefox webkit', workflow)
        self.assertIn('python3 -m unittest tools.tests.test_rc_cycle78_preview_selector -q', workflow)


if __name__ == '__main__':
    unittest.main()
