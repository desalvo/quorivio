"""Cycle 52 B4 global SLO evidence; no network or cluster access."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.aggregate_load_500 import reconcile, reconcile_slo

ROOT = Path(__file__).resolve().parents[2]


def shard(i: int, n: int = 5, *, join: float = 100.0,
          snapshot: float = 200.0, peak: int | None = None) -> dict:
    count = len(range(i, 500, n))
    return {'shard': i, 'shards': n, 'target_total': 500, 'target_shard': count,
            'anonymous_joins': count, 'websocket_completed': count, 'errors': 0,
            'presenter_peak_distinct': peak, 'ramp_seconds': 40,
            'hold_seconds': 90, 'elapsed_seconds': 135,
            'join_latency_samples_ms': [join] * count,
            'first_snapshot_samples_ms': [snapshot] * count,
            'join_latency_ms': {'p50': join, 'p95': join, 'p99': join},
            'first_snapshot_ms': {'p50': snapshot, 'p95': snapshot, 'p99': snapshot}}


def reports() -> list[dict]:
    return [shard(i, peak=490 if i == 0 else None) for i in range(5)]


class GlobalSLOTests(unittest.TestCase):
    def test_complete_five_shard_pass(self):
        r = reconcile_slo(reports())
        self.assertTrue(r['pass'])
        self.assertEqual(r['slo']['sampled_participants'], 500)
        self.assertEqual(r['slo']['join_p95_ms'], 100)
        self.assertEqual(r['slo']['first_snapshot_p95_ms'], 200)

    def test_global_percentile_is_not_average_of_shard_p95s(self):
        data = reports()
        data[0] = shard(0, join=11000, peak=490)
        # Four fast shards cannot erase the 100 slow participants.
        result = reconcile_slo(data)
        self.assertFalse(result['pass'])
        self.assertEqual(result['slo']['join_p95_ms'], 11000)
        self.assertLess(sum(r['join_latency_ms']['p95'] for r in data) / 5, 5000)

    def test_single_slow_client_does_not_alter_p95(self):
        data = reports()
        data[0]['join_latency_samples_ms'][0] = 15000
        data[0]['join_latency_ms']['p99'] = 15000 # Deliberately incorrect: 99/100 remain fast
        self.assertRaises(ValueError, reconcile_slo, data)
        # A single expensive operation is allowed by a p95 SLO, if properly reported.
        data[0]['join_latency_ms']['p99'] = 100
        data[0]['join_latency_ms']['p50'] = 100
        data[0]['join_latency_ms']['p95'] = 100
        self.assertTrue(reconcile_slo(data)['pass'])

    def test_missing_samples_do_not_claim_a_slo(self):
        data = reports()
        del data[2]['join_latency_samples_ms']
        self.assertRaises(ValueError, reconcile_slo, data)
        self.assertTrue(reconcile(data)['pass']) # legacy capacity still supported

    def test_partial_sample_population_fails(self):
        data = reports()
        data[2]['first_snapshot_samples_ms'].pop()
        self.assertRaises(ValueError, reconcile_slo, data)

    def test_invalid_values_are_rejected(self):
        for invalid in (True, float('nan'), float('inf'), -1, '4'):
            data = reports()
            data[0]['join_latency_samples_ms'][0] = invalid
            with self.subTest(invalid=invalid):
                self.assertRaises(ValueError, reconcile_slo, data)

    def test_inconsistent_shard_p95_fails(self):
        data = reports()
        data[1]['join_latency_ms']['p95'] = 200
        self.assertRaises(ValueError, reconcile_slo, data)

    def test_short_hold_and_inflated_elapsed_fails(self):
        data = reports()
        data[0]['hold_seconds'] = 59
        self.assertRaises(ValueError, reconcile_slo, data)
        data = reports()
        data[0]['elapsed_seconds'] = 110
        self.assertRaises(ValueError, reconcile_slo, data)

    def test_error_or_missing_presenter_observer_fails(self):
        data = reports()
        data[0]['errors'] = 1
        self.assertFalse(reconcile_slo(data)['pass'])
        data = reports()
        data[0]['presenter_peak_distinct'] = None
        self.assertFalse(reconcile_slo(data)['pass'])

    def test_reject_invalid_slo_limits(self):
        for key, value in [('max_join_p95_ms', 0),('max_snapshot_p95_ms',float('nan')),
                           ('min_hold_seconds',False)]:
            with self.subTest(key=key):
                self.assertRaises(ValueError, reconcile_slo, reports(), **{key:value})

    def test_multi_shard_cli_accepts_strict_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for i, report in enumerate(reports()):
                p=Path(directory)/f'{i}.json'
                p.write_text(json.dumps(report))
                paths.append(str(p))
            cmd = [sys.executable, str(ROOT/'tools/aggregate_load_500.py'),
                   *paths, '--strict-slo']
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertTrue(json.loads(process.stdout)['pass'])
            report = json.loads(Path(paths[0]).read_text())
            report['first_snapshot_latency_ms'] = 9000 # no effect: raw samples checked
            report['first_snapshot_samples_ms'] = [9000] * 100
            report['first_snapshot_ms']={'p50':9000,'p95':9000,'p99':9000}
            Path(paths[0]).write_text(json.dumps(report))
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            self.assertEqual(process.returncode, 2)
            self.assertFalse(json.loads(process.stdout)['pass'])

    def test_workflow_opt_in_and_does_not_replace_existing_gate(self):
        yml=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('capacity_slo_test:', yml)
        self.assertIn('inputs.capacity_slo_test',yml)
        self.assertIn('python3 tools/ci_capacity_500.py --strict-slo',yml)
        self.assertIn('if: github.event_name == \'workflow_dispatch\' && inputs.capacity_test',yml)
        self.assertIn('run: python3 tools/ci_capacity_500.py\n',yml)
        loader=(ROOT/'tools/load_500.py').read_text()
        self.assertIn("'--latency-samples'",loader)
        self.assertNotIn("'participant_ids'",loader)


if __name__ == '__main__': unittest.main()
