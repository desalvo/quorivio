"""Cycle 34 evidence-scoped acceptance and source guard regressions."""
from __future__ import annotations
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from verify_rc_cycle57_inventory import verify_source,load_inventory

class Cycle34Evidence(unittest.TestCase):
 def test_new_credit_is_bounded_and_does_not_duplicate_old_gates(self):
  matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  gates={g['id']:g for g in matrix['gates']}
  self.assertEqual((audit()['score'],len(gates),preflight()['accepted_gates'],len(preflight()['unaccepted_gates'])),(81.25,53,36,17))
  self.assertEqual(sum(g['weight'] for g in gates.values()),100)
  self.assertEqual((gates['C4']['weight'],gates['C4']['status']),(2,'partial'))
  self.assertEqual((gates['B4']['weight'],gates['B4']['status']),(1,'partial'))
  for name,job in [('C4-AV-INSTREAM',124037870523),('B4-KIND-INGRESS-RECOVERY',124038997005)]:
   child=gates[name]
   self.assertEqual((child['weight'],child['status'],child['verified_run_id'],child['verified_job_id']),(1,'accepted',41048187760,job))
   self.assertEqual(child['verified_commit_sha'],'f5ccf9a7545e7c17b4323d067db66aff5eca9b41')
  self.assertEqual((gates['B4-LOAD']['weight'],gates['C4-PROFILE']['weight']),(2,2))
  self.assertEqual(gates['D3']['status'],'partial')
  self.assertEqual((gates['D3']['weight'],gates['D4']['weight']),(0.5,2))
  self.assertFalse(preflight()['release_candidate_ready'])
  r=matrix['rc_cycle34_verified_reconciliation_20261030']
  self.assertEqual(r['score_after']-r['baseline_score'],1)
  self.assertFalse(r['real_csi_rwx_verified'])
  self.assertFalse(r['production_managed_clamav_uploads_verified'])
 def test_new_scanner_pins_inode_and_rejects_change(self):
  source=(ROOT/'apps/api/src/malware-scan.ts').read_text()
  self.assertIn('constants.O_NOFOLLOW',source)
  self.assertIn('constants.O_NONBLOCK',source)
  self.assertIn('source.createReadStream',source)
  self.assertIn('final.mtimeNs!==initial.mtimeNs',source)
  self.assertIn('antivirus_file_changed',source)
 def test_current_source_is_inventory_complete(self):
  self.assertEqual(verify_source(),len(load_inventory()))
 def test_workflow_checks_historical_and_current_receipts_before_credential_scan(self):
  wf=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertLess(wf.index('verify_rc_cycle33_inventory.py --historical'),wf.index('verify_rc_cycle41_inventory.py'))
  self.assertLess(wf.index('verify_rc_cycle41_inventory.py'),wf.index('Detect credential leaks'))

if __name__=='__main__':unittest.main()
