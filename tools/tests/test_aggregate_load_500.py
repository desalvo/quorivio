"""Pure offline tests; no traffic to external endpoints."""
import unittest
from tools.aggregate_load_500 import reconcile


def shard(i, n=5, *, peak=None):
    allocated = len(range(i, 500, n))
    return {'shard': i, 'shards': n, 'target_total': 500,
            'target_shard': allocated, 'anonymous_joins': allocated,
            'websocket_completed': allocated, 'errors': 0,
            'presenter_peak_distinct': peak}


class AggregateLoadTests(unittest.TestCase):
    def test_five_shards_with_observer(self):
        result = reconcile([shard(i, peak=490 if i == 0 else None) for i in range(5)])
        self.assertTrue(result['pass'])
        self.assertEqual(result['websocket_completed'], 500)
    def test_no_observer_cannot_claim_capacity(self):
        self.assertFalse(reconcile([shard(i) for i in range(5)])['pass'])
    def test_peak_below_threshold(self):
        self.assertFalse(reconcile([shard(i, peak=474 if i == 0 else None) for i in range(5)])['pass'])
    def test_missing_shard_fails(self):
        with self.assertRaises(ValueError): reconcile([shard(i) for i in range(4)])
    def test_duplicate_shard_fails(self):
        with self.assertRaises(ValueError): reconcile([shard(0)]*5)
    def test_negative_and_impossible_metrics(self):
        for key, value in [('errors',-1),('anonymous_joins',101),('websocket_completed',101)]:
            reports=[shard(i) for i in range(5)]
            reports[0][key]=value
            with self.subTest(key=key), self.assertRaises(ValueError): reconcile(reports)
    def test_multiple_observers_rejected(self):
        with self.assertRaises(ValueError): reconcile([shard(i,peak=500 if i<2 else None) for i in range(5)])
    def test_all_complete_but_error_fails(self):
        reports=[shard(i, peak=500 if i==0 else None) for i in range(5)]
        reports[2]['errors']=1
        self.assertFalse(reconcile(reports)['pass'])


    def test_invalid_latency_rejected(self):
        reports=[shard(i,peak=500 if i==0 else None) for i in range(5)]
        for bad in (-1, float('nan'), True, float('inf')):
            reports[0]['join_latency_ms']={'p50':bad,'p95':10,'p99':20}
            with self.subTest(bad=bad), self.assertRaises(ValueError): reconcile(reports)
    def test_nonmonotonic_latency_rejected(self):
        reports=[shard(i,peak=500 if i==0 else None) for i in range(5)]
        reports[0]['first_snapshot_ms']={'p50':50,'p95':30,'p99':100}
        with self.assertRaises(ValueError): reconcile(reports)

if __name__=='__main__':unittest.main()
