#!/usr/bin/env python3
"""Offline reconciliation of Quorivio 500-participant shard reports.

The aggregate is deliberately conservative: separate shard summaries cannot
prove globally distinct concurrent WebSocket identities or presenter peak.
"""
import argparse
import json
import math
import sys
from pathlib import Path


def reconcile(reports, *, expected=500):
    if not reports:
        raise ValueError('at least one shard report is required')
    if not isinstance(expected, int) or not 1 <= expected <= 500:
        raise ValueError('expected participants must be between 1 and 500')
    first = reports[0]
    shards = first.get('shards')
    total = first.get('target_total')
    if type(shards) is not int or shards <= 0 or shards > 500 or total != expected:
        raise ValueError('invalid or inconsistent shard topology')
    if len(reports) != shards:
        raise ValueError(f'expected {shards} shard reports, received {len(reports)}')
    seen = set()
    joins = sockets = errors = 0
    peaks = []
    for r in reports:
        index = r.get('shard')
        if r.get('shards') != shards or r.get('target_total') != total:
            raise ValueError('inconsistent shard topology')
        if type(index) is not int or index < 0 or index >= shards or index in seen:
            raise ValueError('duplicate or invalid shard index')
        seen.add(index)
        assigned = len(range(index, total, shards))
        if type(r.get('target_shard')) is not int or r['target_shard'] != assigned:
            raise ValueError('incorrect shard participant allocation')
        for field in ('anonymous_joins', 'websocket_completed', 'errors'):
            if type(r.get(field)) is not int or r[field] < 0:
                raise ValueError(f'invalid metric: {field}')
        if r['anonymous_joins'] > assigned or r['websocket_completed'] > r['anonymous_joins']:
            raise ValueError('impossible join/WebSocket counts')
        joins += r['anonymous_joins']
        sockets += r['websocket_completed']
        errors += r['errors']
        for metric in ('join_latency_ms', 'first_snapshot_ms'):
            latency=r.get(metric)
            if latency is not None:
                if not isinstance(latency,dict) or set(latency)!={'p50','p95','p99'}:
                    raise ValueError(f'invalid {metric} summary')
                values=[latency[k] for k in ('p50','p95','p99')]
                if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in values if v is not None):
                    raise ValueError(f'invalid {metric} values')
                if any(values[i] is not None and values[i+1] is not None and values[i]>values[i+1] for i in range(2)):
                    raise ValueError(f'nonmonotonic {metric} percentiles')
        peak = r.get('presenter_peak_distinct')
        if peak is not None:
            if type(peak) is not int or not 0 <= peak <= total:
                raise ValueError('invalid presenter peak')
            peaks.append(peak)
    # A single presenter observer, not per-shard snapshots added together.
    if len(peaks) > 1:
        raise ValueError('multiple presenter observers; cannot reconcile a global peak')
    peak = peaks[0] if peaks else None
    passed = joins == total and sockets == total and errors == 0 and peak is not None and peak >= (total * 95 + 99)//100
    return {'target_total': total, 'shards': shards, 'anonymous_joins': joins,
            'websocket_completed': sockets, 'reported_errors': errors,
            'presenter_peak_distinct': peak, 'pass': passed,
            'limitations': ['Reported presenter peak must be observed on a single shared session',
                            'HTTP/WS acceptance does not certify quiz submission latency, privacy or multi-replica correctness',
                            'Shard reports are self-reported; operator must verify staging server metrics and timestamps']}


def _nearest_rank(values: list[float], percentile: int) -> float:
    if not values:
        raise ValueError('empty latency sample population')
    ordered = sorted(values)
    return round(ordered[math.ceil(len(ordered) * percentile / 100) - 1], 1)


def reconcile_slo(reports, *, expected=500, max_join_p95_ms=5000,
                  max_snapshot_p95_ms=8000, min_hold_seconds=60):
    """Fail-closed SLO evidence using *every* numeric client sample across shards.

    Per-shard p95 values must never be averaged: that is not a global percentile.
    No tokens, session IDs, usernames or answers are needed in the evidence.
    """
    base = reconcile(reports, expected=expected)
    limits = (max_join_p95_ms, max_snapshot_p95_ms, min_hold_seconds)
    if any(type(v) not in (float, int) or not math.isfinite(v) or v <= 0 for v in limits):
        raise ValueError('SLO limits and minimum hold must be positive finite numbers')
    join = []
    snapshot = []
    for report in reports:
        ramp = report.get('ramp_seconds')
        hold = report.get('hold_seconds')
        elapsed = report.get('elapsed_seconds')
        if any(type(x) not in (float, int) or not math.isfinite(x) or x < 0
               for x in (ramp, hold, elapsed)):
            raise ValueError('missing or invalid measured load duration')
        if hold < min_hold_seconds or elapsed + 0.2 < ramp + hold:
            raise ValueError('SLO run does not cover the required hold period')
        for field, dest, count_key, summary in (
            ('join_latency_samples_ms', join, 'anonymous_joins', 'join_latency_ms'),
            ('first_snapshot_samples_ms', snapshot, 'websocket_completed', 'first_snapshot_ms')
        ):
            samples = report.get(field)
            if not isinstance(samples, list) or len(samples) != report[count_key]:
                raise ValueError(f'missing or incomplete {field}')
            if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in samples):
                raise ValueError(f'invalid {field} values')
            if not samples:
                raise ValueError(f'empty {field}')
            advertised = report.get(summary)
            if not isinstance(advertised, dict):
                raise ValueError(f'missing {summary} percentiles')
            # Recompute source reports as well as global quantiles; an inconsistent
            # report must not receive a favourable global result.
            if any(advertised.get(f'p{p}') is None or
                   abs(advertised[f'p{p}'] - _nearest_rank(samples, p)) > 0.11
                   for p in (50, 95, 99)):
                raise ValueError(f'contradictory {summary} percentiles')
            dest.extend(samples)
    if len(join) != expected or len(snapshot) != expected:
        raise ValueError('SLO evidence must cover every independent participant')
    join_p95 = _nearest_rank(join, 95)
    snapshot_p95 = _nearest_rank(snapshot, 95)
    passed = bool(base['pass'] and join_p95 <= max_join_p95_ms
                  and snapshot_p95 <= max_snapshot_p95_ms)
    return {**base, 'pass': passed,
            'slo': {'join_p95_ms': join_p95, 'first_snapshot_p95_ms': snapshot_p95,
                    'max_join_p95_ms': max_join_p95_ms,
                    'max_first_snapshot_p95_ms': max_snapshot_p95_ms,
                    'minimum_hold_seconds': min_hold_seconds,
                    'sampled_participants': len(join), 'slo_pass': passed},
            'limitations': base['limitations'] + [
                'Per-client latency samples prove only this disposable run, not an external availability SLO',
                'No actual packet loss, public TLS, physically independent hosts or failure injection is certified',
                'Verify server CPU/memory, client/device distributions and run reproducibility independently']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('reports', nargs='+', type=Path)
    p.add_argument('--expected', type=int, default=500)
    p.add_argument('--json-out', type=Path)
    p.add_argument('--strict-slo', action='store_true', help='Fail closed unless all numeric samples and 60s hold show global p95 within limits')
    p.add_argument('--max-join-p95-ms', type=float, default=5000)
    p.add_argument('--max-snapshot-p95-ms', type=float, default=8000)
    args = p.parse_args()
    try:
        shards = [json.loads(f.read_text(encoding='utf-8')) for f in args.reports]
        report = (reconcile_slo(shards, expected=args.expected,
                 max_join_p95_ms=args.max_join_p95_ms,
                 max_snapshot_p95_ms=args.max_snapshot_p95_ms) if args.strict_slo
                 else reconcile(shards, expected=args.expected))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    output = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    print(output, end='')
    if args.json_out:
        args.json_out.write_text(output, encoding='utf-8')
    return 0 if report['pass'] else 2

if __name__ == '__main__':
    sys.exit(main())
