import test from 'node:test';
import assert from 'node:assert/strict';
import {createLivePeriodicRefresh,DEFAULT_LIVE_REFRESH_CONCURRENCY,validLiveRefreshConcurrency} from '../src/live-periodic-refresh.ts';

const deferred=()=>{let resolve!:()=>void;let reject!:(reason:Error)=>void;const promise=new Promise<void>((ok,no)=>{resolve=ok;reject=no});return {promise,resolve,reject}};

test('RC58: safe bounded concurrency rejects fractional, zero and uncontrolled DB fanout',()=>{
 assert.equal(DEFAULT_LIVE_REFRESH_CONCURRENCY,8);
 for(const n of [0,-1,1.5,33,Number.NaN,Number.POSITIVE_INFINITY])
  assert.throws(()=>validLiveRefreshConcurrency(n),RangeError);
 assert.equal(validLiveRefreshConcurrency(32),32);
 assert.throws(()=>createLivePeriodicRefresh({activeSessions:()=>[],readAndSend:async()=>{},maxConcurrent:1000}),RangeError);
});

test('RC58: 500 distinct active sessions never exceed eight concurrent database snapshots',async()=>{
 const gate=deferred();let active=0, peak=0, started=0;
 const sessions=Array.from({length:500},(_,i)=>`S-${i}`);
 const pump=createLivePeriodicRefresh({activeSessions:()=>sessions,readAndSend:async()=>{started++;peak=Math.max(peak,++active);await gate.promise;active--}});
 const first=pump.tick();
 assert.equal(peak,8);assert.equal(started,8);assert.equal(pump.pendingCount(),8);
 await pump.tick();assert.equal(started,8,'overlapping timer must not schedule another 500 queries');
 gate.resolve();await first;
 assert.equal(started,500);assert.equal(active,0);assert.equal(peak,8);assert.equal(pump.pendingCount(),0);
 await pump.tick();assert.equal(started,1000);
});

test('RC58: slow session never prevents other sessions when pool has spare capacity',async()=>{
 const gate=deferred();const visited:string[]=[];
 const pump=createLivePeriodicRefresh({activeSessions:()=>['slow','fast-a','fast-b'],maxConcurrent:2,readAndSend:async sid=>{
  visited.push(sid);if(sid==='slow')await gate.promise;
 }});
 const run=pump.tick();
 await new Promise<void>(resolve=>queueMicrotask(resolve));
 assert.deepEqual(visited,['slow','fast-a','fast-b']);
 assert.equal(pump.pendingCount(),1);
 gate.resolve();await run;
 assert.equal(pump.pendingCount(),0);
});

test('RC58: a session removed while queued is not read after its client disconnects',async()=>{
 const gate=deferred();const sessions=new Set(['a','b','c']);const visited:string[]=[];
 const pump=createLivePeriodicRefresh({activeSessions:()=>sessions,isSessionActive:sid=>sessions.has(sid),maxConcurrent:1,readAndSend:async sid=>{
  visited.push(sid);if(sid==='a')await gate.promise;
 }});
 const run=pump.tick();sessions.delete('b');gate.resolve();await run;
 assert.deepEqual(visited,['a','c']);
});

test('RC58: rejected reads and logger exceptions cannot starve later sessions',async()=>{
 const attempts:string[]=[];let errors=0;
 const pump=createLivePeriodicRefresh({activeSessions:()=>['one','two','three'],maxConcurrent:1,readAndSend:async sid=>{
  attempts.push(sid);if(sid==='one')throw new Error('db offline');
 },onError:()=>{errors++;throw new Error('logger offline')}});
 await pump.tick();assert.deepEqual(attempts,['one','two','three']);assert.equal(errors,1);
 assert.equal(pump.pendingCount(),0);assert.equal(pump.isRunning(),false);
});

test('RC58: failure enumerating sessions clears running state for recovery',async()=>{
 let n=0;
 const pump=createLivePeriodicRefresh({activeSessions:()=>{if(++n===1)throw new Error('iterator failed');return ['next'];},readAndSend:async()=>{n++}});
 await assert.rejects(pump.tick(),/iterator failed/);
 assert.equal(pump.isRunning(),false);
 await pump.tick();assert.equal(n,3);
});
