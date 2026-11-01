"""RC118: localization of active, ledger-derived completion score is a release invariant."""
from pathlib import Path
import tempfile
import unittest
from tools.rc_gate_audit import audit
from tools.verify_rc_release_status import verify_headers, FILES, FLAGS

ROOT = Path(__file__).resolve().parents[2]


class RC118LocalizedReleaseHeaders(unittest.TestCase):
    def test_full_current_release_headers_match_ledger(self):
        self.assertEqual(verify_headers(ROOT), 4)

    def build_synthetic(self, root, *, it_pct, en_pct):
        docs = root / 'docs'
        docs.mkdir()
        for name in FILES:
            pct = it_pct if name.endswith('.it.md') else en_pct
            # Historical sections are deliberately misleading and must be ignored.
            (docs / name).write_text('# Quorivio 0.1.0-dev RC118 active\n'
                + ' '.join(FLAGS) + f'\nCompletion: {pct}\n\n---\n\n'
                + '# RC118 previous heading\n85,25%\n85.25%\n', encoding='utf8')

    def test_real_chromium_acceptance_tracks_exact_selection_and_modern_palette(self):
        browser=(ROOT/'tools/ci_browser_editor.py').read_text()
        historical=(ROOT/'tools/tests/test_chromium_selection_acceptance_contract.py').read_text()
        source=(ROOT/'apps/web/src/main.tsx').read_text()
        self.assertIn('await select_exact_widget_pair(page)', browser)
        self.assertIn('await checkbox.set_checked(label in wanted)', browser)
        self.assertIn('len(checked_rows)==2', browser)
        self.assertIn("set(selected_ids)=={'widget-a','widget-b'}", browser)
        self.assertIn("await expect(page.locator('.widget-canvas-item')).to_have_count(5)", browser)
        self.assertIn("await expect(page.locator('.widget-canvas-item')).to_have_count(3)", browser)
        self.assertIn("'shape','line','timer'", browser)
        self.assertIn("assert 'divider' not in kinds", browser)
        self.assertIn("'text','shape','line','timer'", source)
        self.assertNotIn("await checks.nth(0).check()",historical)
        self.assertNotIn("await checks.nth(1).check()",historical)

    def test_rejects_wrong_separator_in_italian_current_section(self):
        score = f"{audit()['score']:.2f}%"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_synthetic(root, it_pct=score, en_pct=score)
            with self.assertRaisesRegex(ValueError, 'localized completion score'):
                verify_headers(root, 118)

    def test_rejects_wrong_separator_in_english_current_section(self):
        score = f"{audit()['score']:.2f}%"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_synthetic(root, it_pct=score.replace('.', ','), en_pct=score.replace('.', ','))
            with self.assertRaisesRegex(ValueError, 'localized completion score'):
                verify_headers(root, 118)

    def test_rejects_stale_or_missing_percentage_without_relying_on_history(self):
        score = f"{audit()['score']:.2f}%"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_synthetic(root, it_pct='81,75%', en_pct=score)
            with self.assertRaisesRegex(ValueError, 'localized completion score'):
                verify_headers(root, 118)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_synthetic(root, it_pct='', en_pct=score)
            with self.assertRaisesRegex(ValueError, 'localized completion score'):
                verify_headers(root, 118)

if __name__ == '__main__':
    unittest.main()
