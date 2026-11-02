#!/usr/bin/env python3
"""Fail-closed release candidate readiness report, without invented sign-offs.

Default mode is diagnostic and safe for every CI push. --strict refuses an RC
when any gate is not accepted or evidence/required files are missing.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from rc_gate_audit import audit, LEDGER, ROOT
from rc_external_evidence import verify_packet

REQUIRED = (
 'README.md', 'README.it.md', 'docs/GDPR.en.md', 'docs/GDPR.it.md',
 'docs/DEVELOPMENT_STATUS.md', 'docs/DEVELOPMENT_STATUS.it.md',
 'docs/RC_GATE_MATRIX.json', '.github/workflows/ci.yml',
 'apps/api/src/schema.sql', 'apps/api/src/asset-erasure.ts',
 'tools/ci_retention_postgres.mjs', 'helm', 'compose.yaml', 'Dockerfile',
)

def preflight(root: Path = ROOT, ledger: Path = LEDGER,
              evidence_dir: Path | None = None, release_commit: str | None = None) -> dict:
    # Explicitly do not infer a gate is accepted from a passing test or CI.
    result = audit() if root == ROOT and ledger == LEDGER else _audit_custom(ledger)
    doc = json.loads(ledger.read_text(encoding='utf-8'))
    missing = [rel for rel in REQUIRED if not (root / rel).exists()]
    unaccepted = [
        {'id': gate['id'], 'area': gate['area'], 'status': gate['status'],
         'remaining': gate['remaining']}
        for gate in doc['gates'] if gate['status'] != 'accepted'
    ]
    # Optional external packet is ALWAYS incomplete by default.  Strict RC
    # cannot be granted solely by editing gate statuses in a JSON ledger.
    proof = {'packet_valid': False, 'reason': 'No independently reviewed evidence packet supplied'}
    if evidence_dir is not None and release_commit is not None:
        proof = verify_packet(evidence_dir, ledger_path=ledger, expected_commit=release_commit)
    elif evidence_dir is not None:
        proof = {'packet_valid': False, 'reason': 'Exact reviewed release commit missing'}
    return {'release_candidate_ready': not missing and not unaccepted and proof['packet_valid'],
            'score': result['score'], 'external_evidence': proof, 'missing_required_files': missing,
            'unaccepted_gates': unaccepted, 'gate_count': len(doc['gates']),
            'accepted_gates': len(doc['gates']) - len(unaccepted),
            'policy': 'RC requires every gate accepted with reviewed evidence; local tests alone never promote gates.'}

def _audit_custom(ledger: Path) -> dict:
    from rc_gate_audit import VALID
    doc=json.loads(ledger.read_text(encoding='utf-8'))
    assert sum(g['weight'] for g in doc['gates']) == 100
    assert all(g['status'] in VALID and g.get('evidence') and g.get('remaining') for g in doc['gates'])
    return {'score':round(sum(g['weight']*VALID[g['status']] for g in doc['gates']),2)}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true', help='fail unless every RC gate is accepted')
    parser.add_argument('--output', type=Path, help='write JSON report to this path')
    parser.add_argument('--evidence-dir', type=Path,
                        help='private external-review packet directory (not stored in Git)')
    parser.add_argument('--commit', help='exact reviewed 40-character commit SHA')
    args=parser.parse_args()
    evidence_dir = args.evidence_dir or (Path(os.environ['QUORIVIO_RC_EVIDENCE_DIR'])
                      if os.environ.get('QUORIVIO_RC_EVIDENCE_DIR') else None)
    expected_commit = args.commit or os.environ.get('GITHUB_SHA')
    if args.strict and (evidence_dir is None or not expected_commit):
        parser.error('--strict requires evidence dir and reviewed commit (or QUORIVIO_RC_EVIDENCE_DIR and GITHUB_SHA)')
    report=preflight(evidence_dir=evidence_dir, release_commit=expected_commit)
    rendered=json.dumps(report,indent=2,ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(rendered+'\n',encoding='utf-8')
    return 0 if not args.strict or report['release_candidate_ready'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
