"""CI failure regression contracts for 2026-10-29 (standard + extended)."""
import json
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_rc_cycle12_inventory import load_inventory as load_historical
from verify_rc_cycle13_inventory import MANIFEST, load_inventory
from verify_rc_cycle14_inventory import load_inventory as load_cycle14
from verify_rc_cycle16_inventory import load_inventory as load_cycle16
from verify_rc_cycle18_inventory import load_inventory as load_cycle18
from verify_rc_cycle19_inventory import load_inventory as load_cycle19
from verify_rc_cycle27_inventory import verify_source as verify_current_source, load_inventory as load_current

ROOT = Path(__file__).resolve().parents[2]

class Ci4079Hotfix(unittest.TestCase):
    def test_historical_manifest_remains_immutable_and_current_is_new(self):
        legacy = load_historical()
        self.assertEqual(len(legacy), 790)
        self.assertIn('docs/validation/RC_WIDGET_STYLE_LOCAL_BUILD_TESTS_20261027.log', legacy)
        current = load_inventory()
        self.assertGreaterEqual(len(current), len(legacy))
        self.assertGreaterEqual(len(current),790)  # archived snapshot is intentionally immutable
        self.assertEqual(len(load_cycle14()),800)  # immutable prior receipt
        self.assertEqual(len(load_cycle16()),805)
        self.assertEqual(len(load_cycle18()),823)  # immutable historical snapshot
        self.assertEqual(len(load_cycle19()), 832)  # immutable cycle-19 evidence
        self.assertEqual(verify_current_source(),len(load_current()))
        doc = json.loads((ROOT / MANIFEST).read_text(encoding='utf-8'))
        self.assertEqual(doc['version'], '0.1.0-dev')

    def test_log_receipt_is_not_ignored_by_git(self):
        ignore = (ROOT / '.gitignore').read_text(encoding='utf-8')
        self.assertIn('*.log',ignore)
        self.assertIn('!docs/validation/RC_WIDGET_STYLE_LOCAL_BUILD_TESTS_20261027.log',ignore)
        self.assertTrue((ROOT/'docs/validation/RC_WIDGET_STYLE_LOCAL_BUILD_TESTS_20261027.log').is_file())

    def test_cookie_modal_is_awaited_not_counted_before_reset_form(self):
        fixture = (ROOT/'tools/ci_recovery_url_chromium.py').read_text(encoding='utf-8')
        self.assertIn('await expect(cookie).to_be_visible(timeout=10000)',fixture)
        self.assertIn('await expect(cookie).to_have_count(0)',fixture)
        self.assertNotIn('if await cookie.count():',fixture)
        self.assertLess(fixture.index('await expect(cookie).to_have_count(0)'),fixture.index("await page.get_by_label('Nuova password"))

    def test_workflow_checks_new_manifest_and_keeps_security_gate(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('python3 tools/verify_rc_cycle14_inventory.py',workflow)
        self.assertIn('gitleaks/gitleaks-action@v2',workflow)
        self.assertIn('python3 tools/ci_recovery_url_chromium.py',workflow)
        self.assertLess(workflow.index('Verify grouped SHA-256 evidence inventory'),workflow.index('Detect credential leaks'))

    def test_no_unverified_promotion(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(matrix['gates']),40)
        self.assertEqual(sum(g['weight'] for g in matrix['gates']),100)
        self.assertGreaterEqual(sum(g['weight']*(1 if g['status']=='accepted' else .5 if g['status']=='partial' else 0) for g in matrix['gates']),74)
        self.assertEqual(matrix['ci_failure_hotfix_20261029']['rc_delta_pp'],0)
        self.assertFalse(matrix['ci_failure_hotfix_20261029']['github_full_ci_green_on_hotfix'])

if __name__ == '__main__': unittest.main()
