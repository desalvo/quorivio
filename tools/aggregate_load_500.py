#!/usr/bin/env python3
"""Offline reconciliation of Quorivio 500-participant shard reports.

The aggregate is deliberately conservative: separate shard summaries cannot
prove globally distinct concurrent WebSocket identities or presenter peak.
"""
import argparse
import json
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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('reports', nargs='+', type=Path)
    p.add_argument('--expected', type=int, default=500)
    p.add_argument('--json-out', type=Path)
    args = p.parse_args()
    try:
        report = reconcile([json.loads(f.read_text(encoding='utf-8')) for f in args.reports], expected=args.expected)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    output = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    print(output, end='')
    if args.json_out:
        args.json_out.write_text(output, encoding='utf-8')
    return 0 if report['pass'] else 2

if __name__ == '__main__':
    sys.exit(main())
