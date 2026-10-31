"""RC65: historical CI acceptance is stable when status headers are prepended."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class HistoricalDocumentationCycle65(unittest.TestCase):
    def test_older_acceptance_tests_never_slice_mutable_status_text(self):
        for name in ('test_rc_cycle35_verified_bootstrap.py',
                     'test_rc_cycle57_live_fanout.py',
                     'test_rc_cycle58_reconciliation_and_backpressure.py'):
            source = (ROOT/'tools/tests'/name).read_text()
            tree = ast.parse(source)
            with self.subTest(test=name):
                # Reject read_text()[:N] even if the slicing is deeply nested.
                prefix_slices = [node for node in ast.walk(tree)
                                 if isinstance(node, ast.Subscript)
                                 and isinstance(node.value, ast.Call)
                                 and isinstance(node.value.func, ast.Attribute)
                                 and node.value.func.attr == 'read_text'
                                 and isinstance(node.slice, ast.Slice)
                                 and node.slice.lower is None
                                 and isinstance(node.slice.upper, ast.Constant)]
                self.assertEqual(prefix_slices, [])

    def test_dedicated_historical_evidence_has_the_original_run(self):
        for lang in ('en', 'it'):
            receipt = (ROOT/f'docs/RC58_VERIFIED_IDLE_SLO_AND_REFRESH.{lang}.md').read_text()
            with self.subTest(language=lang):
                self.assertIn('41152939003', receipt)
                self.assertIn('c0fe7f7b9e41c0295387d84996a7b531b91b69a0', receipt)

    def test_newest_status_header_and_handoff_are_consistent(self):
        for lang in ('', '.it'):
            for name in ('DEVELOPMENT_STATUS', 'COMPLETION_HANDOFF'):
                body=(ROOT/f'docs/{name}{lang}.md').read_text()
                current=body.split('\n---\n', 1)[0]
                with self.subTest(name=name, language=lang):
                    self.assertIn('RC65', current)
                    self.assertIn('81,75%' if lang else '81.75%', current)
                    self.assertIn('rc_strict=false', current)


if __name__ == '__main__':
    unittest.main()
