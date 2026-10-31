"""Cycle22: use remote green evidence, not invented production acceptance."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from verify_rc_cycle21_inventory import load_inventory as previous
from verify_rc_cycle57_inventory import load_inventory, verify_source

SHA='caf6331f15ccf39c218791503b8c6d0ca3503dce'
RUN=40918620911

class Cycle22RemoteReconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        cls.gates={g['id']:g for g in cls.doc['gates']}

    def test_genuine_new_scopes_and_remote_proof(self):
        new={
          'B1-RECONNECT':('B1',2,'reconnect on B'),
          'D2-ENCRYPTED-DR':('D2',2,'AES-256-GCM'),
        }
        for sub,(parent,weight,needle) in new.items():
            with self.subTest(subgate=sub):
                g=self.gates[sub]
                self.assertEqual((g['weight'],g['status']),(weight,'accepted'))
                self.assertEqual((g['verified_run_id'],g['verified_job_id'],g['verified_commit_sha']),
                                 (RUN,123605484902,SHA))
                self.assertIn(needle,g['evidence'])
                self.assertEqual(self.gates[parent]['status'],'partial')
                self.assertGreater(self.gates[parent]['weight'],0)
        self.assertNotEqual(self.gates['B1-RECONNECT']['verified_run_id'],self.gates['B1-WS']['verified_run_id'])
        self.assertNotEqual(self.gates['D2-ENCRYPTED-DR']['verified_run_id'],self.gates['D2-DR']['verified_run_id'])
        self.assertIn('not offsite',self.gates['D2-ENCRYPTED-DR']['evidence'].lower())

    def test_exact_weighted_score_unaccepted_gate_set_and_history(self):
        self.assertEqual(len(self.gates),53)
        self.assertEqual(sum(g['weight'] for g in self.gates.values()),100)
        self.assertEqual((audit()['score'],preflight()['accepted_gates']), (81.25,36))
        self.assertEqual(len(preflight()['unaccepted_gates']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertEqual(self.doc['scoring_reconciliation_20261029_cycle16']['reconciled_score'],77)
        self.assertEqual(self.doc['scoring_reconciliation_20261029_cycle22']['delta_pp'],2.0)
        self.assertEqual(self.doc['last_verified_full_ci']['head_sha'],SHA)
        self.assertEqual(self.doc['last_verified_full_ci']['head_sha'],SHA)
        self.assertFalse(self.doc['pending_local_batch']['new_local_runtime_smoke_promoted'])
        self.assertFalse(self.doc['pending_local_batch']['strict_rc_ready'])

    def test_runtime_job_only_manual_no_publish_or_credit(self):
        body=(ROOT/'.github/workflows/ci.yml').read_text()
        script=(ROOT/'tools/ci_oci_runtime_smoke.sh').read_text()
        for needle in ("inputs.runtime_arch_test",'if: github.event_name == \'workflow_dispatch\' && inputs.runtime_arch_test',
                       'docker/setup-qemu-action@v3','platforms: linux/arm64','platforms: linux/amd64',
                       'bash tools/ci_oci_runtime_smoke.sh quorivio:ci-oci-arm64 arm64',
                       'bash tools/ci_oci_runtime_smoke.sh quorivio:ci-oci-amd64 amd64',
                       'push: false'):
            self.assertIn(needle,body)
        for needle in ('docker network create --internal','--platform "linux/$target"',
                       'process.arch','process.getuid()===0','postgres:18-alpine',
                       '/api/health/ready','/api/health/live','apps/web/dist/index.html',
                       'trap cleanup EXIT','--tmpfs /app/assets:rw,uid=1000,gid=1000,mode=0700'):
            self.assertIn(needle,script)
        self.assertNotIn('--publish ',script)
        self.assertNotIn('docker push ',script)
        self.assertEqual(subprocess.run(['bash','-n',str(ROOT/'tools/ci_oci_runtime_smoke.sh')],capture_output=True).returncode,0)

    def test_invalid_runtime_arguments_fail_before_docker(self):
        shell=str(ROOT/'tools/ci_oci_runtime_smoke.sh')
        for args in (("repo:tag", "unknown"),("bad;echo", "arm64"),("repo:tag",)):
            r=subprocess.run(['bash',shell,*args],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,2,r.stderr)

    def test_historical_snapshot_and_current_source(self):
        self.assertEqual(len(previous()),844)
        self.assertGreater(len(load_inventory()),len(previous()))
        self.assertEqual(verify_source(),len(load_inventory()))

if __name__=='__main__':unittest.main()
