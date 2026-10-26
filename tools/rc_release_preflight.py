#!/usr/bin/env python3
"""Fail-closed release candidate readiness report, without invented sign-offs.

Default mode is diagnostic and safe for every CI push. --strict refuses an RC
when any gate is not accepted or evidence/required files are missing.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from rc_gate_audit import audit, LEDGER, ROOT

REQUIRED = (
 'README.md', 'README.it.md', 'docs/GDPR.en.md', 'docs/GDPR.it.md',
 'docs/DEVELOPMENT_STATUS.md', 'docs/DEVELOPMENT_STATUS.it.md',
 'docs/RC_GATE_MATRIX.json', '.github/workflows/ci.yml',
 'apps/api/src/schema.sql', 'apps/api/src/asset-erasure.ts',
 'tools/ci_retention_postgres.mjs', 'helm', 'compose.yaml', 'Dockerfile',
)

def preflight(root: Path = ROOT, ledger: Path = LEDGER) -> dict:
    # Explicitly do not infer a gate is accepted from a passing test or CI.
    result = audit() if root == ROOT and ledger == LEDGER else _audit_custom(ledger)
    doc = json.loads(ledger.read_text(encoding='utf-8'))
    missing = [rel for rel in REQUIRED if not (root / rel).exists()]
    unaccepted = [
        {'id': gate['id'], 'area': gate['area'], 'status': gate['status'],
         'remaining': gate['remaining']}
        for gate in doc['gates'] if gate['status'] != 'accepted'
    ]
    return {'release_candidate_ready': not missing and not unaccepted,
            'score': result['score'], 'missing_required_files': missing,
            'unaccepted_gates': unaccepted, 'gate_count': len(doc['gates']),
            'accepted_gates': len(doc['gates']) - len(unaccepted),
            'policy': 'RC requires every gate accepted with reviewed evidence; local tests alone never promote gates.'}

def _audit_custom(ledger: Path) -> dict:
    from rc_gate_audit import VALID
    doc=json.loads(ledger.read_text(encoding='utf-8'))
    assert sum(g['weight'] for g in doc['gates']) == 100
    assert all(g['status'] in VALID and g.get('evidence') and g.get('remaining') for g in doc['gates'])
    return {'score':round(sum(g['weight']*VALID[g['status']] for g in doc['gates']),1)}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true', help='fail unless every RC gate is accepted')
    parser.add_argument('--output', type=Path, help='write JSON report to this path')
    args=parser.parse_args()
    report=preflight()
    rendered=json.dumps(report,indent=2,ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(rendered+'\n',encoding='utf-8')
    return 0 if not args.strict or report['release_candidate_ready'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
