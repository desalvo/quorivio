"""RC136 independent acceptance evidence: honest, immutable and non-attesting."""
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from rc_external_evidence import FACETS, expected_gates, new_packet, verify_packet
from rc_release_preflight import preflight

SHA = 'a' * 40


class ExternalEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.path.joinpath('attachments').mkdir()
        self.packet = new_packet(SHA)

    def write(self):
        (self.path / 'reviews.json').write_text(json.dumps(self.packet), encoding='utf-8')

    def approve(self):
        for review in self.packet['reviews']:
            gate = review['gate_id']
            review.update(operator='Primary tester', independent_reviewer='Independent assessor',
                          reviewed_at=datetime.now(timezone.utc).isoformat(),
                          environment='Two independently operated physical machines',
                          review_scope='Independent end to end audit of ' + gate,
                          outcome='pass', independent_approval=True,
                          notes='Reproduced against release SHA in isolated real environment')
            for facet in FACETS[gate]:
                relative = f'attachments/{gate}_{facet}.txt'
                payload = f'Physical evidence for {gate}/{facet}'.encode('utf8')
                (self.path / relative).write_bytes(payload)
                review['artifacts'][facet] = {'path': relative, 'sha256': hashlib.sha256(payload).hexdigest()}
        self.write()

    def test_exactly_seventeen_independent_reviews_mapped(self):
        self.assertEqual(len(FACETS),17)
        self.assertEqual(set(FACETS), set(expected_gates()))
        self.assertEqual(len(self.packet['reviews']), 17)
        self.assertTrue(all(v['outcome']=='pending' and not v['independent_approval']
                            for v in self.packet['reviews']))

    def test_no_packet_never_certifies_release(self):
        result=verify_packet(self.path, expected_commit=SHA)
        self.assertFalse(result['packet_valid'])
        self.assertFalse(result['certifies_release'])
        self.assertEqual(len(result['pending']),17)
        self.assertFalse(preflight()['release_candidate_ready'])

    def test_unreviewed_packet_fails_closed(self):
        self.write()
        result=verify_packet(self.path, expected_commit=SHA)
        self.assertFalse(result['packet_valid'])
        self.assertEqual(len(result['pending']),17)
        self.assertTrue(any('independent review' in p for p in result['problems']))

    def test_positive_fixture_verifies_integrity_but_never_certifies(self):
        self.approve()
        result=verify_packet(self.path, expected_commit=SHA)
        self.assertTrue(result['packet_valid'], result['problems'])
        self.assertEqual(result['verified_reviews'],17)
        self.assertFalse(result['certifies_release'])
        report=preflight(evidence_dir=self.path, release_commit=SHA)
        self.assertFalse(report['release_candidate_ready'])
        self.assertEqual(len(report['unaccepted_gates']),17)
        self.assertTrue(report['external_evidence']['packet_valid'])

    def test_commit_replay_fails(self):
        self.approve()
        result=verify_packet(self.path, expected_commit='b'*40)
        self.assertFalse(result['packet_valid'])
        self.assertTrue(any('does not match' in x for x in result['problems']))

    def test_evidence_tampering_detected(self):
        self.approve()
        (self.path / self.packet['reviews'][0]['artifacts']['touch-device']['path']).write_text('changed')
        result=verify_packet(self.path, expected_commit=SHA)
        self.assertFalse(result['packet_valid'])
        self.assertIn('A1',result['pending'])
        self.assertTrue(any('SHA-256 mismatch' in x for x in result['problems']))

    def test_reviewer_cannot_be_operator(self):
        self.approve()
        self.packet['reviews'][0]['independent_reviewer'] = 'PRIMARY TESTER'
        self.write()
        result=verify_packet(self.path, expected_commit=SHA)
        self.assertFalse(result['packet_valid'])
        self.assertTrue(any('distinct named' in x for x in result['problems']))

    def test_review_must_be_timezone_aware_and_not_future(self):
        self.approve()
        self.packet['reviews'][0]['reviewed_at'] = '2026-11-02T10:00:00'
        self.write()
        self.assertFalse(verify_packet(self.path, expected_commit=SHA)['packet_valid'])
        self.packet['reviews'][0]['reviewed_at'] = (datetime.now(timezone.utc)+timedelta(days=2)).isoformat()
        self.write()
        self.assertFalse(verify_packet(self.path, expected_commit=SHA)['packet_valid'])

    def test_path_traversal_and_symlink_blocked(self):
        self.approve()
        ref=self.packet['reviews'][0]['artifacts']['touch-device']
        ref['path']='attachments/../../outside.txt'
        self.write()
        self.assertFalse(verify_packet(self.path, expected_commit=SHA)['packet_valid'])
        external=self.path.parent/'not-in-packet-evidence.txt'
        external.write_text('external')
        self.addCleanup(lambda:external.unlink(missing_ok=True))
        link=self.path/'attachments'/'link.txt'
        link.symlink_to(external)
        ref['path']='attachments/link.txt'
        ref['sha256']=hashlib.sha256(b'external').hexdigest()
        self.write()
        self.assertFalse(verify_packet(self.path, expected_commit=SHA)['packet_valid'])

    def test_reused_attachment_disallowed(self):
        self.approve()
        a=self.packet['reviews'][0]['artifacts']
        a['visual-parity']=dict(a['touch-device'])
        self.write()
        result=verify_packet(self.path, expected_commit=SHA)
        self.assertFalse(result['packet_valid'])
        self.assertTrue(any('reused' in x for x in result['problems']))

    def test_unknown_missing_duplicate_gate_rejected(self):
        self.approve()
        self.packet['reviews'].append(copy.deepcopy(self.packet['reviews'][0]))
        self.write()
        self.assertFalse(verify_packet(self.path, expected_commit=SHA)['packet_valid'])
        self.packet['reviews'][-1]['gate_id']='UNKNOWN'
        self.write()
        self.assertFalse(verify_packet(self.path, expected_commit=SHA)['packet_valid'])
        self.packet['reviews'].pop()
        self.packet['reviews'].pop()
        self.write()
        self.assertFalse(verify_packet(self.path, expected_commit=SHA)['packet_valid'])

    def test_missing_facet_rejected(self):
        self.approve()
        del self.packet['reviews'][3]['artifacts']['voiceover']
        self.write()
        self.assertFalse(verify_packet(self.path, expected_commit=SHA)['packet_valid'])

    def test_cli_fails_without_sha_or_completed_reviews(self):
        script=ROOT/'tools/rc_external_evidence.py'
        creation=subprocess.run([sys.executable,str(script),'--init',str(self.path/'review'),'--commit',SHA],capture_output=True,text=True)
        self.assertEqual(creation.returncode,0,creation.stderr)
        check=subprocess.run([sys.executable,str(script),'--check',str(self.path/'review'),'--expected-commit',SHA],capture_output=True,text=True)
        self.assertEqual(check.returncode,2)
        self.assertIn('"packet_valid": false',check.stdout)
        try_again=subprocess.run([sys.executable,str(script),'--init',str(self.path/'review'),'--commit',SHA],capture_output=True)
        self.assertNotEqual(try_again.returncode,0)

    def test_strict_release_requires_external_evidence(self):
        report=preflight()
        self.assertIn('external_evidence',report)
        self.assertFalse(report['external_evidence']['packet_valid'])
        self.assertFalse(report['release_candidate_ready'])

if __name__=='__main__': unittest.main()

class ExternalEvidenceAttachment(unittest.TestCase):
 def test_import_and_refusal_to_overwrite_or_import_secrets(self):
  from rc_external_evidence import import_attachment
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);d=root/'packet';d.mkdir();(d/'attachments').mkdir()
   (d/'reviews.json').write_text(json.dumps(new_packet('a'*40)))
   src=root/'redacted-report.pdf';src.write_bytes(b'%PDF-operator-redacted-test')
   rel=import_attachment(d,'A4','nvda',src)
   self.assertEqual(rel,'attachments/A4_nvda.pdf')
   obj=json.loads((d/'reviews.json').read_text())
   record=next(x for x in obj['reviews'] if x['gate_id']=='A4')
   self.assertEqual(record['artifacts']['nvda']['sha256'],hashlib.sha256(src.read_bytes()).hexdigest())
   with self.assertRaises(ValueError):import_attachment(d,'A4','nvda',src)
   self.assertEqual((d/rel).read_bytes(),src.read_bytes())
   secret=root/'.env';secret.write_text('PRIVATE_API_KEY=abc')
   with self.assertRaises(ValueError):import_attachment(d,'A4','voiceover',secret)
   with self.assertRaises(ValueError):import_attachment(d,'BAD','voiceover',src)
