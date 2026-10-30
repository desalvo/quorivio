"""Current source inventory and immutable cycle29 catalog."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from verify_rc_cycle45_inventory import verify_source,load_inventory
from verify_rc_cycle29_inventory import load_inventory as historical
class Cycle30Integrity(unittest.TestCase):
 def test_current_tree_matches_new_manifest(self):
  self.assertEqual(verify_source(),len(load_inventory()))
 def test_previous_receipt_kept_separately(self):
  self.assertGreaterEqual(len(historical()),890)
 def test_gate_score_does_not_include_unexecuted_operations(self):
  from rc_gate_audit import audit
  self.assertEqual(audit()['score'],80.75)
if __name__=='__main__':unittest.main()
