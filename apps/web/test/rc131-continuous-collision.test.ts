import test from 'node:test';
import assert from 'node:assert/strict';
import {moveWidgetsToCollisionLimit,overlapsOtherWidgets} from '../src/widget-placement.ts';
const w=(id:string,x:number,y:number,width:number,height:number,kind='text')=>({id,kind,position:{x,y,width,height,rotation:0}});
test('RC138: dragging through narrow neighbours is intentional, independent of pointer speed',()=>{
 const items=[w('moving',2,10,5,10),w('thin',30.05,10,.05,12)];
 assert.equal(moveWidgetsToCollisionLimit(items,['moving'],95,0)[0].position.x,95);
 assert.equal(items[0].position.x,2);
});
test('RC138: pointer motion preserves diagonal deltas, even through another layer',()=>{
 const items=[w('m',10,10,8,8),w('b',30,30,4,4)];
 const out=moveWidgetsToCollisionLimit(items,['m'],70,70);
 assert.deepEqual([out[0].position.x,out[0].position.y],[80,80]);
});
test('RC138: negative motion and canvas limits remain bounded',()=>{
 const items=[w('m',70,70,20,20),w('b',30,30,20,20)];
 assert.equal(moveWidgetsToCollisionLimit(items,['m'],-65,0)[0].position.x,5);
 assert.equal(moveWidgetsToCollisionLimit(items,['m'],90,90)[0].position.x,80);
 assert.equal(moveWidgetsToCollisionLimit(items,['m'],90,90)[0].position.y,80);
});
test('RC138: multi-selection stays rigid while overlapping unrelated widgets',()=>{
 const items=[w('a',5,10,10,10),w('b',5,35,10,10),w('block',35,10,5,10)];
 const out=moveWidgetsToCollisionLimit(items,['a','b'],90,0);
 assert.equal(out[0].position.x,90);assert.equal(out[1].position.x,90);
 assert.equal(out[1].position.y-out[0].position.y,25);
 assert.deepEqual(out[2],items[2]);
});
test('RC138: ordinary widgets overlay as freely as graphics',()=>{
 const items=[w('label',12,15,9,10),w('shape',30,15,8,10,'shape'),w('block',55,15,8,10)];
 const out=moveWidgetsToCollisionLimit(items,['label'],70,0);
 assert.equal(out[0].position.x,82);
 assert.equal(overlapsOtherWidgets(out,['label']),false); // geometry diagnostic, no constraint
 const onTop=moveWidgetsToCollisionLimit(items,['label'],40,0);
 assert.equal(overlapsOtherWidgets(onTop,['label']),true);
});
test('RC138: invalid movement and stale IDs remain no-ops',()=>{
 const items=[w('label',10,10,20,10)];
 assert.equal(moveWidgetsToCollisionLimit(items,['label'],Infinity,1),items);
 assert.equal(moveWidgetsToCollisionLimit(items,['missing'],40,0),items);
});
