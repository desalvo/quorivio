"""Cycle 12 current package must be reproducible, preserve its historical base and avoid false RC credit."""
import json
import re
import unittest
from pathlib import Path
from verify_rc_cycle12_inventory import MANIFEST, load_inventory, verify_zip

ROOT=Path(__file__).resolve().parents[2]

class RC12(unittest.TestCase):
    def test_historical_cycle12_integrity_manifest_is_preserved(self):
        d=json.loads((ROOT/MANIFEST).read_text(encoding='utf8'))
        self.assertEqual(d['version'],'0.1.0-dev')
        self.assertEqual(d['baseline_files_preserved'],782)
        self.assertEqual(d['file_count_excluding_manifest'],len(load_inventory()))
        # Cycle 12 is an immutable archive receipt, not a checksum for later
        # commits. The current tree is verified by the current-cycle manifest.
        self.assertIn('docs/validation/RC_WIDGET_STYLE_LOCAL_BUILD_TESTS_20261027.log',load_inventory())

    def test_secret_scanner_safe_reconstructible_digests(self):
        raw=(ROOT/MANIFEST).read_text(encoding='utf8')
        self.assertNotRegex(raw,r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')
        self.assertGreater(len(load_inventory()),781)
        self.assertTrue(all(re.fullmatch('[0-9a-f]{64}',digest) for digest in load_inventory().values()))

    def test_independent_gate_signoff_is_explicitly_not_claimed(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text(encoding='utf8'))
        self.assertGreaterEqual(len(matrix['gates']),40)
        self.assertEqual(sum(g['weight'] for g in matrix['gates']),100)
        self.assertGreaterEqual(sum(g['weight']*(1 if g['status']=='accepted' else .5 if g['status']=='partial' else 0) for g in matrix['gates']),74)
        evidence=matrix['rc_cycle12_native_browser_and_accessibility_20261029']
        self.assertEqual(evidence['delta_pp'],0)
        self.assertFalse(evidence['rc_ready'])
        self.assertIn('PENDING',evidence['native_firefox_webkit_status'])

if __name__=='__main__':unittest.main()
