"""Regression: avoid false-positive API credentials in historical checksum inventory."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from tools.verify_rc_checksum_manifest import decode_sha256_words, validate_manifest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'docs' / 'RC_DASHBOARD_WIDGET_APPEARANCE_MANIFEST.json'


class HistoricalChecksumManifestTests(unittest.TestCase):
    def test_all_sha256_digests_are_complete_and_reconstructible(self):
        hashes = validate_manifest(SOURCE)
        self.assertEqual(len(hashes), 634)
        for name, digest in hashes.items():
            with self.subTest(name=name):
                self.assertRegex(digest, r'\A[0-9a-f]{64}\Z')

    def test_no_unbroken_api_key_shaped_hex_strings_in_manifest(self):
        raw = SOURCE.read_text(encoding='utf-8')
        self.assertNotIn('"sha256_by_file"', raw)
        values = json.loads(raw)['sha256_hex_groups_by_file']
        self.assertTrue(all(len(part) == 8 for words in values.values() for part in words))
        self.assertFalse(any(re.search(r'[0-9a-f]{32,}', part) for words in values.values() for part in words), 'accidentally restored raw high-entropy checksums')

    def test_rejects_truncated_and_corrupted_digest_words(self):
        for item in ([], ['deadbeef'] * 7, ['deadbeef'] * 7 + ['insecure'], ['deadbeef'] * 7 + [None]):
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    decode_sha256_words(item)

    def test_legacy_manifest_form_fails_closed(self):
        document = json.loads(SOURCE.read_text(encoding='utf-8'))
        document['sha256_by_file'] = document.pop('sha256_hex_groups_by_file')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'legacy.json'
            path.write_text(json.dumps(document), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'unsafe legacy'):
                validate_manifest(path)

    def test_entry_count_is_checked(self):
        document = json.loads(SOURCE.read_text(encoding='utf-8'))
        document['total_count'] += 1
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'invalid.json'
            path.write_text(json.dumps(document), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'entry count'):
                validate_manifest(path)


if __name__ == '__main__':
    unittest.main()
