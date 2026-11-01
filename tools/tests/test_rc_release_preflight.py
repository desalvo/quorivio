import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0,str(ROOT/'tools'))
from rc_release_preflight import preflight

class ReleasePreflightTest(unittest.TestCase):
 def test_current_release_not_accepted(self):
  report=preflight()
  self.assertFalse(report['release_candidate_ready'])
  ledger=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text(encoding='utf-8'))
  earned=sum(g['weight']*{'accepted':1, 'partial':.5, 'open':0, 'blocked':0}[g['status']] for g in ledger['gates'])
  self.assertEqual(report['score'],round(earned,2))
  self.assertEqual({g['id'] for g in report['unaccepted_gates']},
                   {g['id'] for g in ledger['gates'] if g['status']!='accepted'})
  self.assertGreater(len(report['unaccepted_gates']),0)
  self.assertEqual(report['missing_required_files'],[])
 def test_missing_file_blocks_release(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'docs').mkdir();(root/'docs/RC_GATE_MATRIX.json').write_text((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
   report=preflight(root,root/'docs/RC_GATE_MATRIX.json')
   self.assertFalse(report['release_candidate_ready'])
   self.assertIn('Dockerfile',report['missing_required_files'])
 def test_forged_accepted_gates_without_files_are_not_sufficient(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'docs').mkdir(); ledger=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
   for gate in ledger['gates']:gate['status']='accepted'
   f=root/'docs/RC_GATE_MATRIX.json';f.write_text(json.dumps(ledger))
   report=preflight(root,f)
   self.assertEqual(report['score'],100)
   self.assertFalse(report['release_candidate_ready'])
 def test_retention_requires_session_owner(self):
  source=(ROOT/'apps/api/src/server.ts').read_text()
  route=source.split("app.patch('/api/sessions/:id/retention'",1)[1].split("app.delete('/api/sessions/:id'",1)[0]
  self.assertIn("s.owner_id!==auth(req)",route)
  self.assertIn("owner_required",route)
 def test_bad_gate_weight_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'docs').mkdir();ledger=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text());ledger['gates'][0]['weight']=999
   f=root/'docs/RC_GATE_MATRIX.json';f.write_text(json.dumps(ledger))
   with self.assertRaises(AssertionError):preflight(root,f)

if __name__=='__main__':unittest.main()
