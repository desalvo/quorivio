import test from 'node:test';
import assert from 'node:assert/strict';
import {createLivePeriodicRefresh} from '../src/live-periodic-refresh.ts';

const deferred=()=>{let resolve!:()=>void;let reject!:(reason:Error)=>void;const promise=new Promise<void>((ok,no)=>{resolve=ok;reject=no});return {promise,resolve,reject}};

test('RC56: no active sessions implies no database reads',async()=>{
 const visits:string[]=[];
 const pump=createLivePeriodicRefresh({activeSessions:()=>[],readAndSend:async sid=>{visits.push(sid)}});
 await pump.tick();await pump.tick();assert.deepEqual(visits,[]);assert.equal(pump.pendingCount(),0);
});
test('RC56: 500 subscribers in one session cause one refresh, not 500',async()=>{
 let clients=500,reads=0;const pump=createLivePeriodicRefresh({activeSessions:()=>Array(clients).fill('session-A'),readAndSend:async()=>{reads++}});
 await pump.tick();assert.equal(reads,1);await pump.tick();assert.equal(reads,2);
});
test('RC56: simultaneous timer ticks cannot double-read the same session',async()=>{
 const latch=deferred();let reads=0;
 const pump=createLivePeriodicRefresh({activeSessions:()=>['one'],readAndSend:()=>{reads++;return latch.promise}});
 const first=pump.tick();assert.equal(pump.pendingCount(),1);
 await pump.tick();assert.equal(reads,1);
 latch.resolve();await first;assert.equal(pump.pendingCount(),0);
 await pump.tick();assert.equal(reads,2);
});
test('RC56: independent sessions refresh concurrently and exactly once',async()=>{
 let reads:string[]=[];
 const pump=createLivePeriodicRefresh({activeSessions:()=>['one','two','one','three'],readAndSend:async sid=>{reads.push(sid)}});
 await pump.tick();assert.deepEqual(reads.sort(),['one','three','two']);
});
test('RC56: a failed snapshot never certifies freshness and allows retry',async()=>{
 let attempts=0;const faults:string[]=[];
 const pump=createLivePeriodicRefresh({activeSessions:()=>['one'],readAndSend:async()=>{if(++attempts===1)throw new Error('PostgreSQL unavailable')},onError:(_err,sid)=>faults.push(sid)});
 await pump.tick();assert.equal(attempts,1);assert.deepEqual(faults,['one']);assert.equal(pump.pendingCount(),0);
 await pump.tick();assert.equal(attempts,2);assert.equal(pump.pendingCount(),0);
});
test('RC56: logger exceptions cannot permanently stop snapshot heartbeats',async()=>{
 let attempts=0;
 const pump=createLivePeriodicRefresh({activeSessions:()=>['one'],readAndSend:async()=>{if(++attempts===1)throw new Error('db')},onError:()=>{throw new Error('logger')}});
 await pump.tick();await pump.tick();assert.equal(attempts,2);assert.equal(pump.pendingCount(),0);
});
test('RC56: removed sessions are no longer refreshed',async()=>{
 const active=new Set(['one','two']);const reads:string[]=[];
 const pump=createLivePeriodicRefresh({activeSessions:()=>active,readAndSend:async sid=>{reads.push(sid)}});
 await pump.tick();active.delete('one');await pump.tick();assert.deepEqual(reads,['one','two','two']);
});
