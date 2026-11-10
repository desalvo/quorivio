import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createLiveResultPoller} from '../src/live-result-poller.ts';

test('RC300 serializes overlapping ticks and keeps completion order',async()=>{
 let release!:(value:number)=>void;
 const first=new Promise<number>(resolve=>{release=resolve});
 let calls=0;const seen:number[]=[];
 const poll=createLiveResultPoller(async()=>++calls===1?first:2,x=>seen.push(x),()=>assert.fail('unexpected failure'));
 const pending=poll.refresh();assert.equal(await poll.refresh(),false);assert.equal(calls,1);
 release(1);assert.equal(await pending,true);assert.deepEqual(seen,[1]);
 await poll.refresh();assert.deepEqual(seen,[1,2]);assert.equal(calls,2);poll.stop();
});
test('RC300 transient failures do not erase last valid totals and retry succeeds',async()=>{
 let attempt=0,shown=0,warnings=0;
 const poll=createLiveResultPoller(async()=>{attempt++;if(attempt===2)throw Error('offline');return attempt===1?3:4},x=>shown=x,()=>warnings++);
 await poll.refresh();assert.equal(shown,3);
 await poll.refresh();assert.equal(shown,3);assert.equal(warnings,1);
 await poll.refresh();assert.equal(shown,4);poll.stop();
});
test('RC300 stopped sources discard late successful and failed reads',async()=>{
 let done!:(x:number)=>void;
 const deferred=new Promise<number>(r=>{done=r});let commits=0,errors=0;
 const poll=createLiveResultPoller(()=>deferred,()=>commits++,()=>errors++);
 const request=poll.refresh();poll.stop();done(9);await request;
 assert.equal(commits,0);assert.equal(await poll.refresh(),false);
 let fail!:(x:Error)=>void;
 const rejected=new Promise<number>((_,r)=>{fail=r});
 const other=createLiveResultPoller(()=>rejected,()=>commits++,()=>errors++);
 const late=other.refresh();other.stop();fail(Error('offline'));await late;
 assert.equal(commits,0);assert.equal(errors,0);
});
test('RC300 React presenter uses the single-flight coordinator and retains stale counts',()=>{
 const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 const slice=ui.slice(ui.indexOf('function PresenterLinkedResult('),ui.indexOf('/** Guidance is intentionally independent'));
 assert.ok(slice.includes('createLiveResultPoller('));
 assert.ok(slice.includes('poller.stop()'));assert.ok(slice.includes('window.clearInterval(timer)'));
 assert.ok(slice.includes('setLoadFailed(true)'));
 assert.ok(!slice.includes('setRows([]);setLoadFailed(true)'), 'do not clear valid totals on disconnect');
 assert.ok(!slice.includes('setInterval(()=>void load()'), 'avoid bypassing single-flight coordination');
});
