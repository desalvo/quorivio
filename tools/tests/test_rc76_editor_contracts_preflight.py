"""RC76: regression guards must run before expensive CI services and stay fail-closed."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text()


class RC76EarlyContracts(unittest.TestCase):
    def test_editor_contract_preflight_is_before_npm_install(self):
        expected = [
            'tools.tests.test_rc_cycle43_frontend_compile',
            'tools.tests.test_rc_dashboard_widget_appearance_20261027',
            'tools.tests.test_rehearsal_timed_deadline_20261028',
            'tools.tests.test_session_rehearsal',
            'tools.tests.test_topic_linked_results_rc_20261028',
        ]
        first = WORKFLOW.index('Validate evolving editor contracts before npm')
        install = WORKFLOW.index('name: Install reproducibly')
        self.assertLess(first, install)
        for name in expected:
            self.assertIn(name, WORKFLOW[first:install])

    def test_all_historical_receipts_and_only_latest_are_current(self):
        from sys import path
        import importlib
        path.insert(0, str(ROOT / 'tools'))
        guard = importlib.import_module('ci_inventory_reference_guard')
        self.assertGreaterEqual(guard.verify_references(ROOT, enforce_git=False), 1)
        self.assertIn('verify_rc_cycle75_inventory.py --historical', WORKFLOW)
        self.assertIn('verify_rc_cycle76_inventory.py\n', WORKFLOW)

    def test_release_remains_opt_in(self):
        self.assertIn('default: false', WORKFLOW)
        self.assertIn('name: Production publication', WORKFLOW)
        self.assertIn('publish_image', WORKFLOW)

if __name__ == '__main__':
    unittest.main()
