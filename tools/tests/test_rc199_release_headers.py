"""RC199 regression: CI #299 failed because active RC198 status omitted flags."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.verify_rc_release_status import FILES, FLAGS, verify_headers
from tools.verify_rc_current_inventory import current_verifier_module

ROOT = Path(__file__).resolve().parents[2]


class RC199ReleaseHeaderTests(unittest.TestCase):
    def test_actual_four_headers_match_current_cycle_and_safety_flags(self):
        current = current_verifier_module().__name__
        cycle = int(current.split('cycle', 1)[1].split('_', 1)[0])
        self.assertGreaterEqual(cycle, 199)
        self.assertEqual(verify_headers(ROOT), len(FILES))
        for name in FILES:
            active = (ROOT / 'docs' / name).read_text(encoding='utf8').split('\n---\n', 1)[0]
            for flag in FLAGS:
                with self.subTest(file=name, flag=flag):
                    self.assertIn(flag, active)
            self.assertIn(f'RC{cycle}', active.splitlines()[0])

    def test_rc198_omission_is_not_hidden_by_historical_flags(self):
        with tempfile.TemporaryDirectory() as temp:
            docs = Path(temp) / 'docs'
            docs.mkdir()
            for name in FILES:
                (docs / name).write_text('# Quorivio RC199 current\n' + ' '.join(FLAGS) +
                    '\n85,25%\n85.25%\n\n---\n\n# RC198 previous\n' +
                    ' '.join(FLAGS) + '\n', encoding='utf8')
            for file in ('DEVELOPMENT_STATUS.md', 'DEVELOPMENT_STATUS.it.md'):
                p = docs / file
                p.write_text('# Quorivio RC199 current\n85,25%\n85.25%\n'
                    '\n---\n\n# RC198 historical ' + ' '.join(FLAGS), encoding='utf8')
                with self.subTest(file=file):
                    with self.assertRaisesRegex(ValueError, f'{file}: missing one or more explicit release flags'):
                        verify_headers(Path(temp), 199)
                p.write_text('# Quorivio RC199 current\n' + ' '.join(FLAGS) +
                    '\n85,25%\n85.25%\n\n---\n\n# RC198 archived', encoding='utf8')
            self.assertEqual(verify_headers(Path(temp), 199), 4)

    def test_rc198_receipt_retained_and_rc199_current_command(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('python3 tools/verify_rc_cycle198_inventory.py --historical', workflow)
        self.assertIn('python3 tools/verify_rc_cycle199_inventory.py', workflow)
        self.assertIn('tools.tests.test_rc199_release_headers', workflow)
        self.assertTrue((ROOT / 'docs/validation/RC_CYCLE198_PACKAGE_INVENTORY_20261105.json').is_file())


if __name__ == '__main__':
    unittest.main()
