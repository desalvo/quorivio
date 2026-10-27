"""Acceptance ledger validation must not freeze the project progress score.

The score is intentionally allowed to increase as verified RC gates advance.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'rc_gate_audit.py'
spec = importlib.util.spec_from_file_location('rc_gate_audit', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SCORES = {'accepted': 1, 'partial': 0.5, 'open': 0, 'blocked': 0}


class RcGateAuditTests(unittest.TestCase):
    def test_weighted_ledger_is_normalized(self):
        doc = json.loads(module.LEDGER.read_text(encoding='utf-8'))
        gates = doc['gates']
        report = module.audit()
        weights = [g['weight'] for g in gates]
        expected = sum(g['weight'] * SCORES[g['status']] for g in gates)
        self.assertEqual(sum(weights), 100)
        self.assertEqual(report['total_points'], 100)
        self.assertEqual(report['score'], round(expected, 1))
        self.assertEqual(report['accepted_points'], expected)
        self.assertEqual(sum(v['weight'] for v in report['by_area'].values()), 100)
        self.assertEqual(sum(v['points'] for v in report['by_area'].values()), expected)

    def test_unaccepted_gates_derive_from_status_not_a_frozen_list(self):
        doc = json.loads(module.LEDGER.read_text(encoding='utf-8'))
        report = module.audit()
        expected = [g['id'] for g in doc['gates'] if g['status'] != 'accepted']
        self.assertEqual(report['unaccepted'], expected)

    def test_score_moves_with_promotions_without_changing_weights(self):
        # Synthetic ledger proves that changing verified status affects the
        # result, without pinning the actual project at 48% or 53%.
        ledger = {'gates': [
            {'id': 'A4', 'area': 'A-editor', 'weight': 6, 'status': 'open',
             'evidence': 'Synthetic evidence', 'remaining': 'Independent review'},
            {'id': 'D3', 'area': 'D-validation', 'weight': 4, 'status': 'open',
             'evidence': 'Synthetic evidence', 'remaining': 'Platform verification'},
            {'id': 'D1', 'area': 'D-validation', 'weight': 90, 'status': 'accepted',
             'evidence': 'Synthetic evidence', 'remaining': 'Maintenance'},
        ]}
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / 'ledger.json'
            with patch.object(module, 'LEDGER', destination):
                destination.write_text(json.dumps(ledger), encoding='utf-8')
                first = module.audit()
                self.assertEqual(first['score'], 90)
                self.assertEqual(first['unaccepted'], ['A4', 'D3'])
                for gate in ledger['gates'][:2]:
                    gate['status'] = 'partial'
                destination.write_text(json.dumps(ledger), encoding='utf-8')
                second = module.audit()
                self.assertEqual(second['score'], 95)
                self.assertEqual(second['total_points'], 100)
                self.assertEqual(second['by_area']['A-editor']['points'], 3)
                self.assertEqual(second['by_area']['D-validation']['points'], 92)
                self.assertEqual(second['unaccepted'], ['A4', 'D3'])

    def test_unknown_status_or_non_normalized_weight_is_rejected(self):
        ledger = {'gates': [
            {'id': 'A1', 'area': 'A-editor', 'weight': 100, 'status': 'partial',
             'evidence': 'Synthetic evidence', 'remaining': 'Independent review'},
        ]}
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / 'ledger.json'
            with patch.object(module, 'LEDGER', destination):
                ledger['gates'][0]['status'] = 'complete'
                destination.write_text(json.dumps(ledger), encoding='utf-8')
                with self.assertRaises(AssertionError):
                    module.audit()
                ledger['gates'][0]['status'] = 'partial'
                ledger['gates'][0]['weight'] = 99
                destination.write_text(json.dumps(ledger), encoding='utf-8')
                with self.assertRaises(AssertionError):
                    module.audit()


if __name__ == '__main__':
    unittest.main()
