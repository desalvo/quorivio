import importlib.util
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/'rc_gate_audit.py'
spec=importlib.util.spec_from_file_location('rc_gate_audit',SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RcGateAuditTests(unittest.TestCase):
    def test_weighted_ledger_is_normalized(self):
        report=module.audit()
        self.assertEqual(report['total_points'],100)
        self.assertEqual(report['score'],37.5)
        self.assertEqual(sum(v['weight'] for v in report['by_area'].values()),100)
    def test_open_gates_not_claimed_as_accepted(self):
        report=module.audit()
        for key in ('C2','D2','D3','D4','D6'):
            self.assertIn(key,report['unaccepted'])

if __name__=='__main__':unittest.main()
