"""RC240: reproduce and defend CI provenance and private operator-evidence intake."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import rc_external_evidence as ext
from rc_gate_audit import audit
from rc_release_preflight import preflight

ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / 'docs/validation/RC239_FULL_CI_ACCEPTANCE_20261107.json'
MATRIX = ROOT / 'docs/RC_GATE_MATRIX.json'
SHA = '0594b72806a7b6bf27de07a5fb2856747c8fd68d'
RUN = 42284582481
OLD_SHA = 'c0fe7f7b9e41c0295387d84996a7b531b91b69a0'


class RC240FullCIEvidence(unittest.TestCase):
    def test_green_ci_is_current_and_old_receipt_remains_immutable(self):
        matrix = json.loads(MATRIX.read_text())
        receipt = json.loads(CI.read_text())
        self.assertEqual((receipt['run_id'], receipt['head_sha'], receipt['conclusion']), (RUN, SHA, 'success'))
        # RC239 is now an immutable historical receipt, not the current pointer.
        prior=matrix['historical_full_ci_rc239_20261107']
        self.assertEqual((prior['run_id'], prior['head_sha']), (RUN, SHA))
        self.assertEqual(prior['acceptance_receipt'], str(CI.relative_to(ROOT)))
        self.assertEqual(matrix['historical_full_ci_20261031']['head_sha'], OLD_SHA)
        self.assertEqual(matrix['historical_maintainer_confirmed_commit_20261031'], OLD_SHA)
        current=matrix['last_verified_full_ci']
        self.assertEqual((current['run_id'],current['head_sha']),
                         (42382296263,'c108694705d2bd0d8d8444f7840a944b5913e25d'))
        self.assertEqual(matrix['last_maintainer_confirmed_commit'],current['head_sha'])
        self.assertEqual(receipt['github_run_url'], f'https://github.com/desalvo/quorivio/actions/runs/{RUN}')

    def test_all_required_ci_jobs_and_no_inferred_publishing(self):
        report = json.loads(CI.read_text())
        self.assertEqual(report['job_counts'], {'success': 14, 'skipped': 3, 'failed': 0})
        self.assertEqual(len(report['successful_jobs']), 14)
        self.assertEqual(len(report['skipped_jobs']), 3)
        self.assertEqual(len({job['job_id'] for job in report['successful_jobs']+report['skipped_jobs']}), 17)
        self.assertEqual({job['conclusion'] for job in report['successful_jobs']}, {'success'})
        self.assertEqual({job['conclusion'] for job in report['skipped_jobs']}, {'skipped'})
        self.assertEqual(report['campaign_summary']['job_id'], 128130802311)
        self.assertEqual((report['campaign_summary']['required_jobs_passed'], report['campaign_summary']['required_jobs_total']), (11,11))
        self.assertTrue(any('Firefox' in row['name'] for row in report['successful_jobs']))
        self.assertTrue(any('arm64' in row['name'] for row in report['successful_jobs']))
        for key in ('publish_image', 'publish_latest', 'rc_strict'):
            self.assertIs(report[key], False)

    def test_green_ci_does_not_grant_independent_acceptance(self):
        report = json.loads(CI.read_text())
        matrix = json.loads(MATRIX.read_text())
        self.assertEqual(report['external_operator_gates_remaining'], 17)
        self.assertEqual(report['external_operator_reviews_completed_by_this_run'], 0)
        # RC239 itself did NOT publish. RC245 subsequently DID publish the
        # main app image; neither run certifies a separate converter or external reviews.
        self.assertFalse(matrix['historical_full_ci_rc239_20261107']['published_docker_hub'])
        self.assertTrue(matrix['last_verified_full_ci']['published_docker_hub'])
        self.assertFalse(matrix['last_verified_full_ci']['converter_image_published'])
        self.assertEqual(matrix['last_verified_full_ci']['docker_publication_run_id'], 42385404670)
        self.assertEqual(matrix['last_verified_full_ci']['independent_external_reviews_newly_accepted'], 0)
        self.assertEqual((audit()['score'], len(audit()['unaccepted'])), (85.25, 17))
        self.assertEqual((preflight()['accepted_gates'], preflight()['release_candidate_ready']), (43, False))
        self.assertEqual(set(audit()['unaccepted']), set(ext.FACETS))

    def test_no_live_source_hash_swept_into_historical_manifest(self):
        import hashlib
        old = ROOT / 'docs/validation/RC_CYCLE239_PACKAGE_INVENTORY_20261106.json'
        self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(),
                         '6752ab43a1bb52ebc05c42a130602934047cb4134f7226caec73702f698df329')


class RC240EvidenceIntake(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.inbox = self.base / 'reviews'
        self.inbox.mkdir()
        (self.inbox / 'attachments').mkdir()
        self.manifest = self.inbox / 'reviews.json'
        self.manifest.write_text(json.dumps(ext.new_packet(SHA)), encoding='utf-8')
        self.source = self.base / 'redacted.txt'
        self.source.write_text('Sanitized operator evidence for testing\n', encoding='utf-8')
        self.target = self.inbox / 'attachments/A1_touch-device.txt'

    def test_import_pins_regular_inode_and_hashes_exact_written_bytes(self):
        path = ext.import_attachment(self.inbox, 'A1', 'touch-device', self.source)
        self.assertEqual(path, 'attachments/A1_touch-device.txt')
        self.assertEqual(self.target.read_bytes(), self.source.read_bytes())
        self.assertEqual(ext._read_pinned_regular(self.target), hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(next(r for r in json.loads(self.manifest.read_text())['reviews'] if r['gate_id']=='A1')['artifacts']['touch-device']['sha256'], hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_unsafe_source_symlink_swap_after_preflight_refused_and_cleaned(self):
        actual = os.open
        source = self.source
        private = self.base / 'secret.txt'
        private.write_text('Private material that must never be imported')
        def attack(path, flags, *args, **kwargs):
            if Path(path) == source and (flags & os.O_RDONLY) == 0 and (flags & getattr(os, 'O_NOFOLLOW', 0)):
                source.unlink()
                source.symlink_to(private)
            return actual(path, flags, *args, **kwargs)
        before = self.manifest.read_bytes()
        with patch.object(ext.os, 'open', side_effect=attack):
            with self.assertRaises(OSError):
                ext.import_attachment(self.inbox, 'A1', 'touch-device', source)
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertFalse(self.target.exists())

    def test_non_regular_fifo_rejected_without_blocking(self):
        pipe = self.base / 'pipe.txt'
        os.mkfifo(pipe)
        with self.assertRaises(ValueError):
            ext._read_pinned_regular(pipe)

    def test_modified_evidence_is_detected_as_wrong_hash(self):
        ext.import_attachment(self.inbox, 'A1', 'touch-device', self.source)
        self.target.write_text('modified after insertion')
        self.assertNotEqual(ext._read_pinned_regular(self.target),
                            next(r for r in json.loads(self.manifest.read_text())['reviews'] if r['gate_id']=='A1')['artifacts']['touch-device']['sha256'])

    def test_existing_temporary_manifest_is_not_deleted_on_failure(self):
        tmp = self.inbox / 'reviews.json.tmp'
        tmp.write_text('Pre-existing operator data, preserve')
        before = self.manifest.read_bytes()
        with self.assertRaisesRegex(ValueError, 'temporary review file already exists'):
            ext.import_attachment(self.inbox, 'A1', 'touch-device', self.source)
        self.assertEqual(tmp.read_text(), 'Pre-existing operator data, preserve')
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertFalse(self.target.exists())

    def test_manifest_write_failure_rolls_back_temporary_file_and_attachment(self):
        before = self.manifest.read_bytes()
        with patch.object(ext.json, 'dump', side_effect=RuntimeError('disk write interrupted')):
            with self.assertRaisesRegex(RuntimeError, 'disk write interrupted'):
                ext.import_attachment(self.inbox, 'A1', 'touch-device', self.source)
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertFalse(self.target.exists())
        self.assertFalse((self.inbox/'reviews.json.tmp').exists())

    def test_integrity_failure_after_copy_leaves_no_files_or_approval(self):
        original = ext._read_pinned_regular
        def fake(path, copy_to=None):
            value = original(path, copy_to=copy_to)
            return '0'*64 if Path(path)==self.target else value
        before = self.manifest.read_bytes()
        with patch.object(ext, '_read_pinned_regular', side_effect=fake):
            with self.assertRaisesRegex(ValueError, 'destination integrity'):
                ext.import_attachment(self.inbox, 'A1', 'touch-device', self.source)
        self.assertFalse(self.target.exists())
        self.assertEqual(self.manifest.read_bytes(), before)

    def test_operator_template_still_requires_independent_review(self):
        ext.import_attachment(self.inbox, 'A1', 'touch-device', self.source)
        report = ext.verify_packet(self.inbox, expected_commit=SHA)
        self.assertFalse(report['packet_valid'])
        self.assertEqual(len(report['pending']),17)
        self.assertFalse(report['certifies_release'])


if __name__ == '__main__':
    unittest.main()
