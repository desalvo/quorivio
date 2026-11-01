"""Regression for CI 40652684000: visibly drawn rehearsal must remain accessible."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CI=(ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf8')
OFFLINE=(ROOT/'tools/ci_rehearsal_keyboard_chromium.py').read_text(encoding='utf8')
class ChromiumRehearsalPortal(unittest.TestCase):
    def test_modal_is_mounted_into_body_not_inert_editor(self):
        self.assertIn('return createPortal(<div className="rehearsal-backdrop"',UI)
        self.assertIn('aria-modal="true" aria-label="Anteprima interattiva della sessione"',UI)
        self.assertIn('</div></div>,document.body);',UI)
    def test_live_chromium_requires_accessible_role_and_body_parent(self):
        self.assertIn("page.get_by_role('dialog',name='Anteprima interattiva della sessione')",CI)
        self.assertIn('node.parentElement===document.body',CI)
        self.assertIn('node.closest("[inert],[aria-hidden=true]")',CI)
        self.assertIn("await expect(rehearsal.locator('.rehearsal-pane')).to_have_count(2)",CI)
        self.assertNotIn('force=True',CI)
    def test_offline_chromium_checks_portal_and_restoration(self):
        self.assertIn("document.body.appendChild(node)",OFFLINE)
        self.assertIn("node.parentElement===document.body",OFFLINE)
        self.assertIn("node.inert'), 'Closing portal must restore the app root'",OFFLINE)
if __name__=='__main__':unittest.main()
