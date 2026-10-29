"""Conservative RC evidence and actual browser fixture wiring for rehearsal privacy.

Do not promote a local-only UI change or confuse the old full-CI evidence
with an independently accepted real-device/assistive technology test.
"""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[2]
LEDGER=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
EDITOR=(ROOT/'tools/ci_browser_editor.py').read_text()
DOM=(ROOT/'apps/web/src/rehearsal-dialog.ts').read_text()
BROWSER=(ROOT/'tools/ci_rehearsal_keyboard_chromium.py').read_text()

class RehearsalBackgroundAndProfileGate(unittest.TestCase):
    def test_profile_accepted_only_with_actual_prior_chromium_postgres_evidence(self):
        gates={gate['id']:gate for gate in LEDGER['gates']}
        self.assertGreaterEqual(len(gates),33)
        self.assertEqual(sum(gate['weight'] for gate in gates.values()),100)
        self.assertEqual((gates['C4']['weight'],gates['C4']['status']),(3,'partial'))
        self.assertEqual((gates['C4-PROFILE']['weight'],gates['C4-PROFILE']['status']),(2,'accepted'))
        evidence=gates['C4-PROFILE']['evidence']
        for token in ('40638652838','Chromium','PostgreSQL','private','deletion'):
            self.assertIn(token,evidence)
        self.assertIn('RWX',gates['C4']['remaining'])
        self.assertIn('ClamAV',gates['C4']['remaining'])
        self.assertEqual(LEDGER['scoring_reconciliation_20261028_cycle3']['new_score'],61.0)
        self.assertFalse(LEDGER['pending_local_batch']['new_feature_promoted'])

    def test_background_isolation_is_reversible_and_excludes_modal(self):
        for term in ('const modal = root.closest','child !== document.body',
                     'if (sibling === child','sibling.inert = true',
                     "sibling.setAttribute('aria-hidden', 'true')",
                     'node.inert = previous',"node.removeAttribute('aria-hidden')",
                     "node.setAttribute('aria-hidden', ariaHidden)"):
            self.assertIn(term,DOM)
        self.assertIn('get_by_role(\'button\',name=\'Pulsante pagina\')',BROWSER)
        self.assertIn('Pre-existing inert state must remain unchanged',BROWSER)

    def test_opt_in_real_app_mock_checks_both_preview_modes_and_focus(self):
        for term in ('.editor-preview-open.preview-both',
                     "name='Anteprima interattiva della sessione'",
                     "locator('.rehearsal-pane')",
                     "('width',20)",
                     "page.keyboard.press('Escape')",
                     "Editor must be interactive after rehearsal"):
            self.assertIn(term,EDITOR)
        self.assertNotIn('force=True',EDITOR)
        self.assertIn('python3 tools/ci_browser_editor.py', (ROOT/'.github/workflows/ci.yml').read_text())

if __name__=='__main__':unittest.main()
