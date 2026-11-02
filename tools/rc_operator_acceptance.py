#!/usr/bin/env python3
"""Deterministic, non-attesting handoff of remaining RC external acceptances.

No release gate is promoted and no operator sign-off is fabricated. The plan is
regenerated from the scored gate ledger; strict comparison catches stale plans.
"""
from __future__ import annotations

import argparse
import json
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=PLAN)
    parser.add_argument('--check', action='store_true', help='refuse a stale or edited plan')
    args = parser.parse_args()
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
