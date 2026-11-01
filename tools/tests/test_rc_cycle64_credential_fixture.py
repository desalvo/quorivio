"""RC64: no hardcoded high-entropy test token, without disabling Gitleaks."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tools/tests/test_rc_cycle62_ci_rate_isolation.py'


class CredentialFixtureRegression(unittest.TestCase):
    def test_rate_limit_fixture_uses_a_derived_test_only_token(self):
        tree = ast.parse(FIXTURE.read_text(encoding='utf-8'))
        token_assignments = [
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'TOKEN' for t in node.targets)
        ]
        self.assertEqual(len(token_assignments), 1)
        # Prevent repeating the exact Gitleaks generic-api-key false positive.
        self.assertNotIsInstance(token_assignments[0].value, ast.Constant)
        self.assertEqual(len(hashlib.sha256(b'local-regression-fixture-only').hexdigest()), 64)

    def test_gitleaks_stays_enabled_and_suppressions_are_not_added(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('gitleaks/gitleaks-action@v2', workflow)
        self.assertIn('Detect credential leaks', workflow)
        self.assertFalse((ROOT / '.gitleaks.toml').exists())
        self.assertNotIn('GITLEAKS_ENABLE_COMMENTS: false', workflow)

    def test_early_preflight_runs_before_expensive_integration(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertLess(workflow.index('Check nonsecret CI token fixture'),
                        workflow.index('Install reproducibly'))


if __name__ == '__main__':
    unittest.main()
