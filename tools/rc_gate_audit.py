#!/usr/bin/env python3
"""Deterministic acceptance gate ledger. Status must reflect human-reviewed evidence.
Never infer E2E completion just from the presence of source code or passing unit tests.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'docs' / 'RC_GATE_MATRIX.json'
VALID = {'accepted': 1.0, 'partial': 0.5, 'open': 0.0, 'blocked': 0.0}

def audit():
    doc = json.loads(LEDGER.read_text(encoding='utf-8'))
    groups = {}
    total = accepted = 0.0
    for item in doc['gates']:
        assert item['status'] in VALID, item['id']
        assert (type(item['weight']) in (int, float) and math.isfinite(item['weight'])
                and item['weight'] >= 0.5 and item['weight'] * 2 == int(item['weight'] * 2)), item['id']
        assert item.get('evidence') and item.get('remaining'), item['id']
        earned = item['weight'] * VALID[item['status']]
        total += item['weight']
        accepted += earned
        groups.setdefault(item['area'], [0, 0])
        groups[item['area']][0] += earned
        groups[item['area']][1] += item['weight']
    assert math.isclose(total, 100, abs_tol=1e-9), f'weights must total 100; got {total}'
    return {'score': round(accepted, 2), 'accepted_points': accepted,
            'total_points': total, 'by_area': {k: {'points': v[0], 'weight': v[1],
            'percentage': round(100*v[0]/v[1], 1)} for k, v in groups.items()},
            'unaccepted': [x['id'] for x in doc['gates'] if x['status'] != 'accepted']}

if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
