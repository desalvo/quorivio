"""RC147: checksum inventory must be reproducible from clean Git checkouts."""
from __future__ import annotations

import json
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from rc_inventory_closure import is_ephemeral_source_path
from package_rc_cumulative import assemble_paths
from verify_rc_current_inventory import current_verifier_module
PREVIOUS = 'docs/validation/RC_CYCLE146_PACKAGE_INVENTORY_20261103.json'
CURRENT = 'docs/validation/RC_CYCLE147_PACKAGE_INVENTORY_20261103.json'


class InventoryNoCacheTests(unittest.TestCase):
    def test_known_generated_outputs_are_not_source(self):
        for path in (
            'tools/tests/__pycache__/test_rc145_mobile_background_font.cpython-313.pyc',
            'tools/tests/x.pyo', 'node_modules/x/index.js', 'apps/web/dist/index.html',
            '.pytest_cache/v/cache/lastfailed', 'coverage/report.json',
        ):
            with self.subTest(path=path):
                self.assertTrue(is_ephemeral_source_path(path))
        for path in (
            'tools/tests/test_rc145_mobile_background_font.py',
            'docs/validation/RC_CYCLE146_PACKAGE_INVENTORY_20261103.json',
            'docs/validation/RC_WIDGET_STYLE_LOCAL_BUILD_TESTS_20261027.log',
        ):
            with self.subTest(path=path):
                self.assertFalse(is_ephemeral_source_path(path))

    def test_old_cumulative_cache_cannot_be_carried_forward(self):
        prior = json.loads((ROOT / PREVIOUS).read_text(encoding='utf-8'))
        self.assertIn('tools/tests/__pycache__/test_rc145_mobile_background_font.cpython-313.pyc', prior['files_sha256_hex_groups'])
        files = assemble_paths(ROOT, PREVIOUS, current_verifier_module().MANIFEST, [
            'tools/tests/test_rc147_inventory_no_cache.py',
            'tools/verify_rc_cycle147_inventory.py',
        ])
        self.assertTrue(files)
        self.assertFalse(any(is_ephemeral_source_path(name) for name in files))
        self.assertIn(PREVIOUS, files)

    def test_current_inventory_excludes_generated_data_and_is_current(self):
        active = current_verifier_module()
        self.assertGreaterEqual(int(active.MANIFEST.split('CYCLE')[1].split('_')[0]), 148)
        self.assertTrue((ROOT / CURRENT).is_file())
        contents = active.load_inventory()
        self.assertTrue(contents)
        self.assertFalse(any(is_ephemeral_source_path(name) for name in contents))
        self.assertEqual(active.verify_source(), len(contents))
        # The earlier RC147 receipt remains valid as immutable historical data.
        from tools.verify_rc_cycle147_inventory import load_inventory as historic_receipt
        self.assertTrue(historic_receipt(ROOT / CURRENT))

    def test_current_manifest_refuses_generated_file_even_if_it_exists(self):
        active = current_verifier_module()
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'receipt.json'
            file.write_text(json.dumps({
                'version': '0.1.0-dev', 'cycle': 147,
                'file_count_excluding_manifest': 1,
                'files_sha256_hex_groups': {
                    'tools/tests/__pycache__/cached.pyc': ['a' * 8] * 8,
                },
            }), encoding='utf8')
            with self.assertRaisesRegex(ValueError, 'ephemeral generated path'):
                active.load_inventory(file)


if __name__ == '__main__':
    unittest.main()
