#!/usr/bin/env python3
"""Deterministic, non-attesting handoff of remaining RC external acceptances.

No release gate is promoted and no operator sign-off is fabricated. The plan is
regenerated from the scored gate ledger; strict comparison catches stale plans.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / 'docs/RC_GATE_MATRIX.json'
PLAN = ROOT / 'docs/validation/RC127_OPERATOR_ACCEPTANCE_PLAN_20261102.json'

# Each item names the external proof needed. Never turn a CI job into a human,
# provider, physically independent storage, or accessibility certification.
OBJECTIVES = {
 'A1': ('Editor, touchscreen, pixel-parity and concurrent editing', 'Reviewer video or notes from actual mobile/touch/desktop editor, multi-author conflicts and latency'),
 'A2': ('Filmstrip and representative slide fidelity', 'Operator page-order and thumbnail/page image comparisons across desktop and actual touch devices'),
 'A3': ('Editor/presenter/audience real visual parity and Office corpus', 'Reviewed representative PPTX roundtrips, layout diffs and iOS Safari device proof'),
 'A4': ('Real assistive-technology accessibility', 'Independent NVDA, VoiceOver and TalkBack keyboard/focus/contrast audit'),
 'B1': ('Real multi-replica network recovery and latency', 'Long-duration reconnect test under variable latency, outages and independent hosts'),
 'B2': ('Concurrent timed participation and real timing', 'Independent-presenter/participant device timing and multi-replica long-duration trace'),
 'B3': ('Real participant result visualization and accessibility', 'Firefox/WebKit plus physically separate devices and screen-reader result checks'),
 'B4': ('Representative availability and capacity', 'Independent-node CSI/RWX partition/failover trace, memory/latency SLO and operator review'),
 'C1': ('Account recovery via external provider and browser', 'Real SMTP deliverability and concurrent replica recovery with network-loss proof'),
 'C2': ('MFA delivery, outage and recovery', 'Provider SMTP delivery and outage/retry trace across separate API replicas'),
 'C3': ('Actual OAuth/OIDC provider consent', 'Real Google/GitHub/Facebook authorized consent and callback tests including provider outages'),
 'C4': ('Shared assets and scanner operational lifecycle', 'Physical multi-node RWX/ClamAV concurrency, update and key-custody evidence'),
 'D2': ('Offsite encrypted restore RTO/RPO', 'Independently witnessed restore, lost-write window, custody and legal-hold test evidence'),
 'D3': ('Deployment on independent hardware and storage', 'Real multi-host ingress/TLS/CSI RWX plus native ARM64 operation and recovery evidence'),
 'D4': ('Independent security/accessibility/Office review', 'Pentest, AGID accessibility and Microsoft Office fidelity operator reports'),
 'D5': ('Editorially reviewed bilingual manuals', 'IT/EN screenshots and live tasks reviewed by independent end users'),
 'D6': ('GDPR/legal and operational retention assessment', 'Documented privacy/legal review, key rotation, erasure, audit and storage approvals'),
}


def make_plan(ledger_path: Path = GATES) -> dict:
    ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
    pending = [g for g in ledger['gates'] if g['status'] != 'accepted']
    ids = {g['id'] for g in pending}
    if ids - set(OBJECTIVES):
        raise ValueError('RC external acceptance mapping is incomplete or stale: ' +
                         str(sorted(ids - set(OBJECTIVES))))
    return {
        'schema': 'quorivio-rc-external-acceptance-plan-v1',
        'version': ledger['version'],
        'ready_for_rc': False,
        'external_reviews_completed': 0,
        'requires_independent_evidence': True,
        'notice': 'This is an uncompleted review plan, not proof of operator approval or release readiness.',
        'unaccepted_count': len(pending),
        'items': [
            {'id': g['id'], 'area': g['area'], 'weight': g['weight'],
             'status': g['status'], 'objective': OBJECTIVES[g['id']][0],
             'evidence_to_collect': OBJECTIVES[g['id']][1],
             'review_status': 'not_submitted', 'evidence_uri': None,
             'reviewer': None, 'reviewed_at': None,
             'operator_approval': False}
            for g in pending
        ],
    }


# Operator evidence remains separate from external RC approval.
COMMIT_RE = re.compile(r'^[0-9a-f]{40}$')
SHA_RE = re.compile(r'^[0-9a-f]{64}$')


def make_evidence_bundle(commit: str, plan: dict | None = None) -> dict:
    if not COMMIT_RE.fullmatch(commit):
        raise ValueError('Evidence bundle requires an exact 40-character lowercase commit SHA')
    source = plan if plan is not None else make_plan()
    return {
        'schema': 'quorivio-rc-operator-evidence-v1',
        'commit': commit,
        'ready_for_rc': False,
        'independent_approval': False,
        'notice': 'Technical operator evidence only; does not accept RC gates or replace independent review.',
        'items': [
            {
                'id': item['id'],
                'test_status': 'not_run',
                'environment': '',
                'operator': '',
                'notes': '',
                'artifacts': [],
                'independent_approval': False,
            }
            for item in source['items']
        ],
    }


def verify_evidence_bundle(bundle_path: Path, commit: str | None = None,
                           plan: dict | None = None) -> dict:
    """Verify commit binding, all gate IDs, safe file paths and artifact hashes.

    This checks evidence integrity only. It never validates the adequacy of a
    human review, changes RC gate states, or grants an independent sign-off.
    """
    bundle_path = bundle_path.resolve(strict=True)
    data = json.loads(bundle_path.read_text(encoding='utf-8'))
    source = plan if plan is not None else make_plan()
    if data.get('schema') != 'quorivio-rc-operator-evidence-v1':
        raise ValueError('Unsupported evidence bundle schema')
    sha = data.get('commit')
    if not isinstance(sha, str) or not COMMIT_RE.fullmatch(sha) or (commit is not None and sha != commit):
        raise ValueError('Evidence bundle commit mismatch or invalid full SHA')
    if data.get('ready_for_rc') is not False or data.get('independent_approval') is not False:
        raise ValueError('Operator evidence cannot assert independent RC approval')
    entries = data.get('items')
    if not isinstance(entries, list) or [x.get('id') for x in entries if isinstance(x, dict)] != [x['id'] for x in source['items']] or len(entries) != len(source['items']):
        raise ValueError('Evidence bundle gate IDs or ordering do not match the RC plan')
    validated = 0
    for item in entries:
        if item.get('test_status') not in {'not_run', 'pass', 'fail', 'blocked'}:
            raise ValueError('Unsupported technical test status')
        if item.get('independent_approval') is not False:
            raise ValueError('Operator test record cannot grant independent approval')
        if not isinstance(item.get('environment'), str) or not isinstance(item.get('operator'), str) or not isinstance(item.get('notes'), str):
            raise ValueError('Invalid operator metadata')
        artifacts = item.get('artifacts')
        if not isinstance(artifacts, list):
            raise ValueError('Evidence artifacts must be a list')
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                raise ValueError('Invalid evidence artifact')
            rel = artifact.get('path')
            digest = artifact.get('sha256')
            if not isinstance(rel, str) or not rel or not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
                raise ValueError('Invalid evidence path or SHA256')
            relative = Path(rel)
            if relative.is_absolute() or any(part in ('.', '..') for part in relative.parts) or '\\' in rel:
                raise ValueError('Evidence paths must be relative without traversal')
            root = bundle_path.parent
            evidence_file = (root / relative).resolve(strict=True)
            if not evidence_file.is_relative_to(root) or not evidence_file.is_file():
                raise ValueError('Evidence artifact must be a regular file inside the bundle directory')
            if hashlib.sha256(evidence_file.read_bytes()).hexdigest() != digest:
                raise ValueError(f'Evidence SHA256 mismatch: {rel}')
            validated += 1
    return {'commit': sha, 'gates_checked': len(entries), 'artifacts_verified': validated,
            'ready_for_rc': False, 'independent_approval': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=PLAN)
    parser.add_argument('--check', action='store_true', help='refuse a stale or edited plan')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--init-evidence', type=Path, metavar='PATH', help='Create a non-attesting operator evidence bundle')
    group.add_argument('--verify-evidence', type=Path, metavar='PATH', help='Verify evidence artifact SHA256 digests')
    parser.add_argument('--commit', help='Exact full Git SHA for this evidence bundle')
    args = parser.parse_args()
    if args.init_evidence is not None:
        if not args.commit:
            parser.error('--init-evidence requires --commit')
        data = make_evidence_bundle(args.commit)
        args.init_evidence.parent.mkdir(parents=True, exist_ok=True)
        with args.init_evidence.open('x', encoding='utf-8') as target:
            target.write(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        print(f'Initialized {len(data["items"])} unreviewed operator test records')
        return 0
    if args.verify_evidence is not None:
        result = verify_evidence_bundle(args.verify_evidence, commit=args.commit)
        print(json.dumps(result, indent=2))
        return 0
    plan = make_plan()
    serialized = json.dumps(plan, indent=2, ensure_ascii=False) + '\n'
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding='utf-8') != serialized:
            print('External acceptance plan missing, stale or prematurely attested')
            return 1
        print(f'PASS: {len(plan["items"])} unresolved RC operator gates remain unaccepted')
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding='utf-8')
    print(f'Wrote {len(plan["items"])} pending independent operator reviews')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
