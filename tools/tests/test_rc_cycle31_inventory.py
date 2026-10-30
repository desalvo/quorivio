import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from verify_rc_cycle33_inventory import verify_source,load_inventory
from verify_rc_cycle31_inventory import load_inventory as historical
from rc_release_preflight import preflight

class Cycle31Inventory(unittest.TestCase):
    def test_current_files_match(self):
        self.assertEqual(verify_source(),len(load_inventory()))
    def test_immutable_cycle30_catalog_retained(self):
        self.assertEqual(len(historical()),917)
    def test_strict_rc_stays_blocked(self):
        report=preflight()
        self.assertEqual(report['score'],79.25)
        self.assertEqual((report['accepted_gates'],len(report['unaccepted_gates'])),(31,17))
        self.assertFalse(report['release_candidate_ready'])
    def test_workflow_order(self):
        wf=(ROOT/'.github/workflows/ci.yml').read_text()
        a=wf.index('python3 tools/verify_rc_cycle31_inventory.py --historical')
        b=wf.index('python3 tools/verify_rc_cycle33_inventory.py')
        c=wf.index('Detect credential leaks')
        self.assertLess(a,b)
        self.assertLess(b,c)

if __name__=='__main__':unittest.main()
