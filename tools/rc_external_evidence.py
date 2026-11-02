#!/usr/bin/env python3
"""Offline, fail-closed verification of independent RC operator evidence.

The report is a technical integrity/completeness check, NEVER a substitute for
an independent human judgement or a cryptographically signed certification.
Evidence belongs outside the source tree and must not be committed to Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from rc_operator_acceptance import OBJECTIVES
from rc_gate_audit import LEDGER

SCHEMA = 'quorivio-rc-operator-evidence-v1'
REQUIREMENTS = Path(__file__).resolve().parents[1] / 'docs/validation/RC136_OPERATOR_EVIDENCE_REQUIREMENTS_20261102.json'
SHA = re.compile(r'[0-9a-f]{64}\Z')
COMMIT = re.compile(r'[0-9a-f]{40}\Z')
MAX_EVIDENCE_SIZE = 1024 * 1024 * 1024  # 1 GiB per attachment; large recordings supported.
# Each independent facet needs its own tangible, reproducible artefact.  A
# passed CI suite is not a replacement for provider/physical/human evidence.
FACETS = {
    'A1': ('touch-device', 'concurrent-editor', 'visual-parity'),
    'A2': ('thumbnail-comparison', 'physical-touch'),
    'A3': ('office-roundtrip', 'ios-safari', 'three-view-parity'),
    'A4': ('nvda', 'voiceover', 'talkback', 'keyboard-audit'),
    'B1': ('multi-replica-duration', 'network-disruption', 'latency-slo'),
    'B2': ('physical-timer', 'independent-replica-latency'),
    'B3': ('physical-results', 'screenreader-results'),
    'B4': ('independent-csi-rwx', 'partition-failover', 'capacity-slo'),
    'C1': ('external-smtp-recovery', 'cross-replica-recovery'),
    'C2': ('real-smtp-mfa', 'smtp-outage-recovery'),
    'C3': ('google-consent', 'github-consent', 'facebook-consent', 'provider-failure'),
    'C4': ('managed-clamav', 'physical-rwx', 'backup-key-custody'),
    'D2': ('offsite-restore', 'rpo-rto-measurement', 'key-custody', 'legal-hold'),
    'D3': ('physical-arm64', 'independent-ingress-tls', 'real-csi-failover'),
    'D4': ('independent-pentest', 'agid-a11y', 'office-fidelity-review'),
    'D5': ('italian-manual', 'english-manual', 'end-user-review'),
    'D6': ('independent-gdpr-review', 'key-rotation', 'erasure-retention', 'storage-review'),
}


def expected_gates(ledger_path: Path | None = None) -> dict[str, dict]:
    data = json.loads((ledger_path or LEDGER).read_text(encoding='utf-8'))
    ids = {item['id'] for item in data['gates'] if item['status'] != 'accepted'}
    known = {item['id']: item for item in data['gates'] if item['id'] in FACETS}
    if ids - set(FACETS) or set(known) != set(FACETS) or set(FACETS) != set(OBJECTIVES):
        raise ValueError('RC136 facet mapping no longer covers the outstanding independent RC reviews')
    return known


def requirements_document(ledger_path: Path | None = None) -> dict:
    expected = expected_gates(ledger_path)
    return {'schema': 'quorivio-rc-external-evidence-requirements-v1',
            'version': '0.1.0-dev', 'claims_approval': False,
            'gates': [{'id': gate, 'area': item['area'],
                       'objective': OBJECTIVES[gate][0],
                       'facets': list(FACETS[gate])}
                      for gate, item in expected.items()]}


def new_packet(commit: str, ledger_path: Path | None = None) -> dict:
    if not COMMIT.fullmatch(commit):
        raise ValueError('full lowercase 40-character commit SHA required')
    gates = expected_gates(ledger_path)
    return {
        'schema': SCHEMA,
        'version': '0.1.0-dev',
        'release_commit': commit,
        'warning': 'UNREVIEWED TEMPLATE. Fill offline after external reviews; never store secrets or participant data.',
        'reviews': [
            {
                'gate_id': key,
                'operator': '',
                'independent_reviewer': '',
                'reviewed_at': '',
                'environment': '',
                'review_scope': '',
                'outcome': 'pending',
                'independent_approval': False,
                'notes': '',
                'artifacts': {facet: {'path': '', 'sha256': ''} for facet in FACETS[key]},
            }
            for key in gates
        ],
    }


def _timestamp_valid(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        dt = datetime.fromisoformat(value)
        return bool(dt.tzinfo and dt.utcoffset() is not None and
                    dt.astimezone(timezone.utc) <= datetime.now(timezone.utc))
    except ValueError:
        return False


def _artifact_is_safe(evidence_dir: Path, filename: object) -> bool:
    if not isinstance(filename, str) or not filename or '\\' in filename or '\x00' in filename:
        return False
    rel = PurePosixPath(filename)
    if (rel.is_absolute() or '..' in rel.parts or '.' in rel.parts or
            len(rel.parts) < 2 or rel.parts[0] != 'attachments' or
            re.match(r'^[A-Za-z]:', filename)):
        return False
    p = evidence_dir.joinpath(*rel.parts)
    # Reject symlinks even when a final resolved target is inside the inbox.
    if any(x.is_symlink() for x in (p, *p.parents) if x != evidence_dir and evidence_dir in x.parents):
        return False
    try:
        if not p.is_file() or not p.resolve().is_relative_to(evidence_dir.resolve()):
            return False
    except (OSError, RuntimeError):
        return False
    return True


def verify_packet(directory: Path, ledger_path: Path | None = None,
                  expected_commit: str | None = None) -> dict:
    """Return a structured finding, without upgrading any release status."""
    expected = expected_gates(ledger_path)
    issues: list[str] = []
    report = {'schema': SCHEMA, 'packet_valid': False, 'verified_reviews': 0,
              'total_reviews': len(expected), 'pending': [], 'problems': issues,
              'certifies_release': False}
    packet_path = directory / 'reviews.json'
    try:
        if packet_path.is_symlink():
            raise ValueError('manifest cannot be a symlink')
        packet = json.loads(packet_path.read_text(encoding='utf-8'))
    except (OSError, ValueError, UnicodeError) as exc:
        issues.append('reviews.json is missing or invalid: ' + str(exc))
        report['pending'] = list(expected)
        return report
    if not isinstance(packet, dict) or packet.get('schema') != SCHEMA or packet.get('version') != '0.1.0-dev':
        issues.append('packet schema/version mismatch')
        return report
    if not isinstance(packet.get('release_commit'), str) or not COMMIT.fullmatch(packet['release_commit']):
        issues.append('invalid release commit')
    if expected_commit is not None and packet.get('release_commit') != expected_commit:
        issues.append('release commit does not match the source being reviewed')
    records = packet.get('reviews')
    if not isinstance(records, list):
        issues.append('reviews must be an array')
        report['pending'] = list(expected)
        return report
    by_id: dict[str, dict] = {}
    for entry in records:
        if not isinstance(entry, dict) or not isinstance(entry.get('gate_id'), str):
            issues.append('malformed gate review record')
            continue
        gate = entry['gate_id']
        if gate not in expected:
            issues.append('unexpected gate ' + gate[:64])
        elif gate in by_id:
            issues.append('duplicate gate ' + gate)
        else:
            by_id[gate] = entry
    missing = set(expected) - set(by_id)
    issues.extend('missing review for ' + gate for gate in sorted(missing))
    seen_paths: set[str] = set()
    for gate in expected:
        row = by_id.get(gate)
        if row is None:
            report['pending'].append(gate)
            continue
        errs = []
        operator = row.get('operator')
        reviewer = row.get('independent_reviewer')
        if (not isinstance(operator, str) or not operator.strip() or
                not isinstance(reviewer, str) or not reviewer.strip() or
                operator.strip().casefold() == reviewer.strip().casefold()):
            errs.append('two distinct named operator and independent reviewer identities are required')
        if not _timestamp_valid(row.get('reviewed_at')):
            errs.append('reviewed_at must be a non-future timezone-aware timestamp')
        for field in ('review_scope', 'environment', 'notes'):
            if not isinstance(row.get(field), str) or len(row[field].strip()) < 8:
                errs.append(field + ' must contain substantive notes')
        if row.get('outcome') != 'pass' or row.get('independent_approval') is not True:
            errs.append('independent review has not approved the gate')
        artifacts = row.get('artifacts')
        if not isinstance(artifacts, dict) or set(artifacts) != set(FACETS[gate]):
            errs.append('mandatory evidence facets differ from the gate checklist')
        else:
            for facet in FACETS[gate]:
                spec = artifacts.get(facet)
                if not isinstance(spec, dict) or set(spec) != {'path', 'sha256'}:
                    errs.append('invalid artefact entry for ' + facet)
                    continue
                path, digest = spec['path'], spec['sha256']
                if not _artifact_is_safe(directory, path):
                    errs.append('missing/unsafe attachment for ' + facet)
                    continue
                if path in seen_paths:
                    errs.append('attachment reused across facets: ' + facet)
                else:
                    seen_paths.add(path)
                if not isinstance(digest, str) or not SHA.fullmatch(digest):
                    errs.append('invalid SHA-256 for ' + facet)
                    continue
                file = directory / path
                try:
                    if file.stat().st_size == 0 or file.stat().st_size > MAX_EVIDENCE_SIZE:
                        errs.append('empty or oversized attachment for ' + facet)
                    else:
                        h = hashlib.sha256()
                        with file.open('rb') as src:
                            for chunk in iter(lambda: src.read(1024 * 1024), b''):
                                h.update(chunk)
                        if h.hexdigest() != digest:
                            errs.append('SHA-256 mismatch for ' + facet)
                except OSError:
                    errs.append('unreadable attachment for ' + facet)
        if errs:
            report['pending'].append(gate)
            issues.extend(f'{gate}: {issue}' for issue in errs)
        else:
            report['verified_reviews'] += 1
    report['packet_valid'] = not issues and report['verified_reviews'] == len(expected)
    return report



# Only redacted reports/screenshots/screen captures: never import secrets or
# project .env files.  Operators are responsible for redacting PII before use.
SAFE_SUFFIXES = {'.pdf', '.txt', '.md', '.json', '.csv', '.png', '.jpg', '.jpeg',
                 '.webp', '.mp4', '.webm', '.log'}


def import_attachment(directory: Path, gate: str, facet: str, source: Path) -> str:
    """Copy one redacted review attachment atomically; never overwrite evidence."""
    if gate not in FACETS or facet not in FACETS[gate]:
        raise ValueError('unknown external acceptance gate/facet')
    if source.is_symlink() or not source.is_file() or source.suffix.lower() not in SAFE_SUFFIXES:
        raise ValueError('only regular, already-redacted report/screenshot/video files may be attached')
    if not 0 < source.stat().st_size <= MAX_EVIDENCE_SIZE:
        raise ValueError('attachment empty or exceeds the 1 GiB limit')
    manifest = directory / 'reviews.json'
    if manifest.is_symlink():
        raise ValueError('refusing a symlinked review manifest')
    packet = json.loads(manifest.read_text(encoding='utf-8'))
    if (packet.get('schema') != SCHEMA or not isinstance(packet.get('release_commit'), str)
            or not COMMIT.fullmatch(packet['release_commit'])):
        raise ValueError('review packet schema/commit is invalid')
    records = packet.get('reviews')
    if not isinstance(records, list) or len(records) != len(FACETS) or {r.get('gate_id') for r in records} != set(FACETS):
        raise ValueError('review packet does not cover the full gate inventory')
    review = next(r for r in records if r['gate_id'] == gate)
    if set(review.get('artifacts', {})) != set(FACETS[gate]):
        raise ValueError('gate facets have been modified')
    entry = review['artifacts'][facet]
    if entry != {'path': '', 'sha256': ''}:
        raise ValueError('facet already has evidence; do not overwrite reviewed content')
    relative = 'attachments/' + gate + '_' + facet + source.suffix.lower()
    out = directory / relative
    if out.is_symlink() or out.exists() or out.parent.is_symlink():
        raise ValueError('target evidence path already exists or is a symlink')
    out.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    # O_EXCL prevents a racing process from replacing an existing file.
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'wb') as dst, source.open('rb') as src:
            for chunk in iter(lambda: src.read(1024 * 1024), b''):
                dst.write(chunk)
                h.update(chunk)
        entry.update(path=relative, sha256=h.hexdigest())
        tmp = directory / 'reviews.json.tmp'
        if tmp.exists() or tmp.is_symlink():
            raise ValueError('temporary review file already exists')
        with tmp.open('x', encoding='utf-8') as handle:
            json.dump(packet, handle, indent=2, ensure_ascii=False)
            handle.write('\n')
        os.replace(tmp, manifest)
    except BaseException:
        out.unlink(missing_ok=True)
        raise
    return relative


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--init', metavar='DIR', type=Path, help='create private, unapproved operator packet')
    mode.add_argument('--check', metavar='DIR', type=Path, help='verify complete external evidence packet, fail closed')
    mode.add_argument('--report', metavar='DIR', type=Path, help='show missing evidence without claiming approval')
    mode.add_argument('--matrix-check', action='store_true', help='verify facet-to-gate mapping for CI')
    mode.add_argument('--attach', metavar='DIR', type=Path, help='import one redacted evidence file and record its SHA-256')
    parser.add_argument('--commit', help='full source commit SHA (required for --init)')
    parser.add_argument('--expected-commit', help='source SHA required for --check; prevents stale reviews')
    parser.add_argument('--gate', help='gate ID to attach evidence to')
    parser.add_argument('--facet', help='mandatory evidence category to attach')
    parser.add_argument('--file', type=Path, help='redacted file to import')
    args = parser.parse_args(argv)
    if args.attach:
        if not (args.gate and args.facet and args.file) or args.commit or args.expected_commit:
            parser.error('--attach requires --gate, --facet and --file (not --commit)')
        try:
            target = import_attachment(args.attach, args.gate, args.facet, args.file)
        except (ValueError, OSError) as exc:
            parser.error(str(exc))
        print('Attachment recorded with SHA-256:', target)
        print('Gate remains PENDING until the independent reviewer provides a real approval.')
        return 0
    if args.matrix_check:
        if args.expected_commit or args.commit:
            parser.error('matrix check does not accept commit arguments')
        gates = expected_gates()
        if json.loads(REQUIREMENTS.read_text(encoding='utf-8')) != requirements_document():
            raise ValueError('RC136 published operator evidence requirements are stale')
        print('PASS: external evidence facets defined for', len(gates), 'independent gates; no claims of approval')
        return 0
    if args.init:
        if args.expected_commit:
            parser.error('init does not accept --expected-commit')
        if not args.commit:
            parser.error('--init requires --commit')
        p = args.init.resolve()
        if p.exists() and any(p.iterdir()):
            parser.error('refusing to overwrite an existing evidence directory')
        packet = new_packet(args.commit)
        p.mkdir(parents=True, exist_ok=True)
        (p / 'attachments').mkdir()
        (p / 'reviews.json').write_text(json.dumps(packet, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('Created UNAPPROVED external review packet:', p / 'reviews.json')
        print('No RC gate or release status was changed.')
        return 0
    if args.commit:
        parser.error('--commit only applies to --init')
    if args.check and not args.expected_commit:
        parser.error('--check requires --expected-commit')
    if args.expected_commit and not COMMIT.fullmatch(args.expected_commit):
        parser.error('expected commit must be a full lowercase 40-character SHA')
    report = verify_packet(args.check if args.check else args.report, expected_commit=args.expected_commit)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if (args.report or report['packet_valid']) else 2


if __name__ == '__main__':
    sys.exit(main())
