"""RC rehearsal keyboard/scroll acceptance wiring and lifecycle contract."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
DOM=(ROOT/'apps/web/src/rehearsal-dialog.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()
BROWSER=(ROOT/'tools/ci_rehearsal_keyboard_chromium.py').read_text()

class RehearsalKeyboardFocus(unittest.TestCase):
    def test_actual_rehearsal_installs_guard_and_does_not_double_close_on_escape(self):
        self.assertIn("import {activateRehearsalDialog} from './rehearsal-dialog'",UI)
        self.assertIn('activateRehearsalDialog(root,()=>closeRef.current())',UI)
        self.assertIn('tabIndex={-1}',UI)
        self.assertIn('aria-modal="true"',UI)
        self.assertNotIn("onKeyDown={e=>{if(e.key==='Escape')onClose()}}",UI)

    def test_keyboard_guard_restores_invoker_and_prior_scroll(self):
        for clause in ('const invoker = document.activeElement',"document.body.style.overflow = 'hidden'",'document.body.style.overflow = priorOverflow','invoker?.isConnected','event.isComposing','document.removeEventListener',"event.key === 'Escape'",'event.shiftKey && active === first',"getComputedStyle(element).visibility !== 'hidden'"):
            self.assertIn(clause,DOM)

    def test_modal_background_is_inert_without_inerting_the_dialog(self):
        # External screen readers ignore Tab-based focus trapping alone.
        # Isolate siblings along the ancestor chain, not the app root.
        for clause in ('const modal = root.closest', 'const background:', 'sibling.inert = true', "sibling.setAttribute('aria-hidden', 'true')",
                       'node.inert = previous', 'child = parent'):
            self.assertIn(clause, DOM)
        self.assertIn("'Background button leaked into accessible modal view'", BROWSER)
        self.assertIn('Pre-existing inert state must remain unchanged', BROWSER)

    def test_browser_checks_real_compiled_typescript_on_two_viewports(self):
        for clause in ('esbuild.transform','rehearsal-dialog.ts','1440,900','390,844','page.keyboard.press(\'Tab\')',"page.keyboard.press('Shift+Tab')","page.keyboard.press('Escape')",'document.body.style.overflow'):
            self.assertIn(clause,BROWSER)

    def test_opt_in_ci_runs_offline_browser_after_geometry_check(self):
        self.assertIn('python3 tools/ci_rehearsal_keyboard_chromium.py',CI)
        self.assertLess(CI.index('python3 tools/ci_preview_layout_offline.py'),CI.index('python3 tools/ci_rehearsal_keyboard_chromium.py'))

if __name__=='__main__':unittest.main()
