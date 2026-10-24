import test from 'node:test';
import assert from 'node:assert/strict';
import {createLiveSnapshotQueue} from '../src/live-snapshot-queue.ts';
const deferred=()=>{let release!:()=>void;const promise=new Promise<void>(resolve=>{release=resolve});return {promise,release}};
test('coalesces bursts while preserving final snapshot',async()=>{
 const a=deferred(),b=deferred(),seen:number[]=[];let n=0;
 const q=createLiveSnapshotQueue(async()=>{seen.push(++n);if(n===1)await a.promise;else if(n===2)await b.promise});
 const first=q.enqueue('s');void q.enqueue('s').catch(()=>{});void q.enqueue('s').catch(()=>{});assert.deepEqual(seen,[1]);a.release();
 // allow first completion to start the next read
 await new Promise(resolve=>setImmediate(resolve));assert.deepEqual(seen,[1,2]);b.release();await first;
 assert.deepEqual(seen,[1,2]);assert.equal(q.pendingCount(),0);
});
test('sessions have independent reads',async()=>{
 const a=deferred();const seen:string[]=[];
 const q=createLiveSnapshotQueue(async sid=>{seen.push(sid);if(sid==='a')await a.promise});
 const p=q.enqueue('a');await q.enqueue('b');assert.deepEqual(seen,['a','b']);a.release();await p;
});
test('a failed read does not discard newer notifications',async()=>{
 const a=deferred();let count=0,errors=0;
 const q=createLiveSnapshotQueue(async()=>{count++;if(count===1){await a.promise;throw Error('transient')}},()=>{errors++});
 const p=q.enqueue('s');void q.enqueue('s').catch(()=>{});a.release();await assert.rejects(p,/transient/);
 assert.equal(count,2);assert.equal(errors,1);assert.equal(q.pendingCount(),0);
});

test('coalesced callers wait for the latest snapshot rather than reporting premature completion',async()=>{
 const gate=deferred();let reads=0;const q=createLiveSnapshotQueue(async()=>{reads++;if(reads===1)await gate.promise});
 const first=q.enqueue('x');const second=q.enqueue('x');let finished=false;void second.then(()=>{finished=true});
 await new Promise(r=>setImmediate(r));assert.equal(finished,false);gate.release();await Promise.all([first,second]);
 assert.equal(reads,2);assert.equal(finished,true);assert.equal(q.pendingCount(),0);
});
test('failed snapshots reject subscribers and leave the queue reusable',async()=>{
 let calls=0;const q=createLiveSnapshotQueue(async()=>{if(++calls===1)throw Error('database unavailable')});
 await assert.rejects(q.enqueue('x'),/database unavailable/);
 assert.equal(q.pendingCount(),0);await q.enqueue('x');assert.equal(calls,2);
});
