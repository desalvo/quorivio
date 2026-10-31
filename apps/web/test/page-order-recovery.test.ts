import test from 'node:test';
import assert from 'node:assert/strict';
import {commitAndReconcilePageOrder} from '../src/page-order-recovery.ts';
const ids=(v:{ids:string[]})=>v.ids;

test('page reorder acknowledges the canonical persisted order',async()=>{
 const result=await commitAndReconcilePageOrder(['b','a'],async()=>undefined,async()=>({ids:['b','a']}),ids);
 assert.equal(result.state,'saved');assert.deepEqual(result.snapshot.ids,['b','a']);
});
test('lost write response after COMMIT is recovered with readback, not incorrectly rolled back',async()=>{
 let writes=0;
 const result=await commitAndReconcilePageOrder(['b','a'],async()=>{writes++;throw Error('response lost after commit')},async()=>({ids:['b','a']}),ids);
 assert.equal(result.state,'recovered');assert.equal(writes,1);
});
test('rejected write reads unchanged authoritative order without inventing success',async()=>{
 const result=await commitAndReconcilePageOrder(['b','a'],async()=>{throw Error('403')},async()=>({ids:['a','b']}),ids);
 assert.equal(result.state,'rejected');assert.deepEqual(result.snapshot.ids,['a','b']);
});
test('concurrent server reorder wins over outdated response',async()=>{
 const result=await commitAndReconcilePageOrder(['b','a'],async()=>undefined,async()=>({ids:['a','b']}),ids);
 assert.equal(result.state,'concurrent');
});
test('unavailable readback never reports the previous order as confirmed',async()=>{
 await assert.rejects(commitAndReconcilePageOrder(['b','a'],async()=>undefined,async()=>{throw Error('offline')},ids),/offline/);
});
test('invalid or changed page collections fail closed',async()=>{
 await assert.rejects(commitAndReconcilePageOrder(['b','b'],async()=>undefined,async()=>({ids:['a','b']}),ids),/Invalid/);
 await assert.rejects(commitAndReconcilePageOrder(['a','b'],async()=>undefined,async()=>({ids:['a','c']}),ids),/collection changed/);
});
