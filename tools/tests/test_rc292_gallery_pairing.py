#!/usr/bin/env python3
"""RC292: never mix live CI screenshot evidence with old published PDFs.

Current build PDFs and current live captures must be tested together. The
checked-in manuals use the archived, SHA-256 verified RC291 captures, even
when a new Chromium capture was written earlier in the same CI job.
"""
from __future__ import annotations
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.manual_screenshot_catalog import (
    SCREENSHOTS, HISTORIC_SCREENSHOTS, LATEST_ARCHIVED_SCREENSHOTS,
    LATEST_ARCHIVED_COMMIT, evidence, gallery, CATALOG,
)
from tools.tests import test_rc284_manual_pdf_gallery as pdf_gallery_tests
ROOT = Path(__file__).resolve().parents[2]

class RC292GalleryPairing(unittest.TestCase):
    def test_archived_25_real_screens_are_cryptographically_verified(self):
        record=evidence(LATEST_ARCHIVED_SCREENSHOTS,expected_commit=LATEST_ARCHIVED_COMMIT,minimum=25)
        self.assertEqual(len(record['shots']),25)
        self.assertEqual(record['build'],'RC291')
        self.assertEqual(record['fixture'],'synthetic-only')
        self.assertEqual(sum('presenter' in CATALOG[s] for s in record['shots']),17)
        self.assertEqual(sum('user' in CATALOG[s] for s in record['shots']),9)
        self.assertEqual(sum('admin' in CATALOG[s] for s in record['shots']),6)
        self.assertIn('ARCHIVIO RC291', gallery('presenter','it',path=LATEST_ARCHIVED_SCREENSHOTS))
        self.assertNotIn('CURRENT BUILD',gallery('presenter','en',path=LATEST_ARCHIVED_SCREENSHOTS))
        self.assertNotIn('Commit ',gallery('user','it',path=LATEST_ARCHIVED_SCREENSHOTS))

    def test_original_rc283_evidence_still_independently_validates(self):
        historic=evidence(HISTORIC_SCREENSHOTS,
            expected_commit='0bb89e6ac79ed57493130f06fc5042182a166ed6',minimum=13)
        self.assertEqual(len(historic['shots']),13)
        self.assertIn('ARCHIVIO RC283',gallery('presenter','it',path=HISTORIC_SCREENSHOTS))

    def test_broad_test_discovery_uses_checked_in_manuals_with_archive(self):
        output, screenshots, commit=pdf_gallery_tests.RC284ManualPDFGallery.paired_evidence(None,'f'*40)
        self.assertEqual(output,ROOT/'docs/manuals')
        self.assertEqual(screenshots,LATEST_ARCHIVED_SCREENSHOTS)
        self.assertEqual(commit,LATEST_ARCHIVED_COMMIT)
        # Even if CI has already recorded a new live manifest, the local PDF
        # cannot be tested against unrelated new captures.
        with patch('tools.tests.test_rc284_manual_pdf_gallery.SCREENSHOTS',Path('/other/active-capture')):
            output2, source2, _=pdf_gallery_tests.RC284ManualPDFGallery.paired_evidence(None,'b'*40)
            self.assertEqual(output2,output)
            self.assertEqual(source2,screenshots)

    def test_explicit_ci_pdf_output_requires_current_capture_and_commit(self):
        build=Path('/tmp/quorivio-manual-build')
        out,source,sha=pdf_gallery_tests.RC284ManualPDFGallery.paired_evidence(str(build),'e'*40)
        self.assertEqual(out,build)
        self.assertEqual(source,SCREENSHOTS)
        self.assertEqual(sha,'e'*40)
        with self.assertRaisesRegex(ValueError,'Git SHA'):
            pdf_gallery_tests.RC284ManualPDFGallery.paired_evidence(str(build),None)
        with self.assertRaises(ValueError):
            gallery('presenter','it',path=LATEST_ARCHIVED_SCREENSHOTS,
                    require=True,commit=LATEST_ARCHIVED_COMMIT)

    def test_ci_runs_strict_live_pdf_gate_and_early_gallery_pair_preflight(self):
        ci=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('python3 -m unittest tools.tests.test_rc292_gallery_pairing -q',ci)
        self.assertIn('generate_manuals.py --require-real --output-dir /tmp/quorivio-manual-build',ci)
        self.assertIn('QUORIVIO_MANUAL_OUTPUT_DIR=/tmp/quorivio-manual-build python3 -m unittest tools.tests.test_rc284_manual_pdf_gallery -q',ci)
        self.assertLess(ci.index('tools.tests.test_rc292_gallery_pairing'),
                        ci.index('python3 tools/ci_manual_real_screenshots.py'))

if __name__=='__main__': unittest.main()
