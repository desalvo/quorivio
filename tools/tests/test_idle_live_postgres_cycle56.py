"""Deterministic opt-in 70s receiver contracts, no database or network used."""
import asyncio
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
with patch.dict('os.environ',{'QUORIVIO_CI_ADMIN_EMAIL':'admin@example.com','QUORIVIO_CI_NEW_PASSWORD':'fake-fixture-password','QUORIVIO_CI_LOAD_TOKEN':'x'*40}):
    import ci_live_idle_snapshots as probe

class Clock:
    def __init__(self):self.t=0.
    def now(self):return self.t

class Message:
    type=probe.aiohttp.WSMsgType.TEXT
    def __init__(self,session='abc',private=False):self.session=session;self.private=private
    def json(self):
        data={'session':{'id':self.session}}
        if self.private:data['connected_participants']=9
        return {'type':'snapshot','data':data}

class SyntheticSocket:
    def __init__(self,clock,seq):self.clock=clock;self.seq=iter(seq)
    async def receive(self,timeout):
        item=next(self.seq,None)
        if item is None:
            self.clock.t+=timeout
            raise asyncio.TimeoutError
        at,msg=item
        self.clock.t=at
        return msg

class IdleLiveCycle56(unittest.TestCase):
    def test_authoritative_periodic_snapshots_cover_70_seconds(self):
        clock=Clock();ws=SyntheticSocket(clock,[(0,Message()),(20,Message()),(40,Message()),(60,Message())])
        n=asyncio.run(probe.watch_quiet_snapshots(ws,'abc','presenter',now=clock.now))
        self.assertEqual(n,4)

    def test_initial_only_snapshots_fail_closed(self):
        clock=Clock();ws=SyntheticSocket(clock,[(0,Message()),(1,Message())])
        with self.assertRaisesRegex(AssertionError,'no authoritative snapshot'):
            asyncio.run(probe.watch_quiet_snapshots(ws,'abc','presenter',now=clock.now))

    def test_cross_session_snapshot_never_counts(self):
        clock=Clock();ws=SyntheticSocket(clock,[(0,Message('other'))])
        with self.assertRaisesRegex(AssertionError,'wrong-session'):
            asyncio.run(probe.watch_quiet_snapshots(ws,'abc','presenter',now=clock.now))

    def test_participant_presence_stays_private(self):
        clock=Clock();ws=SyntheticSocket(clock,[(0,Message(private=True))])
        with self.assertRaisesRegex(AssertionError,'private presenter presence'):
            asyncio.run(probe.watch_quiet_snapshots(ws,'abc','participant',now=clock.now))

    def test_opt_in_rejects_any_public_origin(self):
        with patch.object(probe,'A','https://demo.example.org'):
            with self.assertRaisesRegex(RuntimeError,'loopback'):
                probe.require_disposable_origins()

    def test_workflow_opt_in_not_standard_ci(self):
        s=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('inputs.live_idle_test',s)
        self.assertIn('run: python3 tools/ci_live_idle_snapshots.py',s)
        self.assertIn('timeout-minutes: 3',s)

if __name__=='__main__':unittest.main()
