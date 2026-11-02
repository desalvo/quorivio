import test from 'node:test';
import assert from 'node:assert/strict';
import {moveWidgetsToCollisionLimit,overlapsOtherWidgets} from '../src/widget-placement.ts';

const w=(id:string,x:number,y:number,width:number,height:number,kind='text')=>({id,kind,position:{x,y,width,height,rotation:0}});

test('RC131: cannot tunnel across a 0.05%-wide widget with a 95%-wide pointer jump',()=>{
 const items=[w('moving',2,10,5,10),w('thin',30.05,10,.05,12)];
 const out=moveWidgetsToCollisionLimit(items,['moving'],95,0);
 assert.ok(out[0].position.x>24.99&&out[0].position.x<=25.0501,JSON.stringify(out));
 assert.equal(overlapsOtherWidgets(out,['moving']),false);
 assert.equal(items[0].position.x,2);
});
test('RC131: continuous diagonal collision maintains identical X/Y progress',()=>{
 const items=[w('m',10,10,8,8),w('b',30,30,4,4)];
 const out=moveWidgetsToCollisionLimit(items,['m'],70,70);
 assert.ok(out[0].position.x>21.98&&out[0].position.x<22.001,JSON.stringify(out));
 assert.ok(Math.abs(out[0].position.x-out[0].position.y)<.0001);
 assert.equal(overlapsOtherWidgets(out,['m']),false);
});
test('RC131: correct behavior when motion only brushes a corner or goes away',()=>{
 const diagonal=moveWidgetsToCollisionLimit([w('m',10,10,8,8),w('b',30,31,2,2)],['m'],12,12);
 assert.equal(diagonal[0].position.x,22);
 const away=moveWidgetsToCollisionLimit([w('m',30,10,10,10),w('b',40,10,8,10)],['m'],-15,0);
 assert.equal(away[0].position.x,15);
});
test('RC131: collision is symmetric for backward and vertical directions',()=>{
 const horizontal=moveWidgetsToCollisionLimit([w('m',70,15,10,10),w('b',22,15,3,10)],['m'],-65,0);
 assert.ok(horizontal[0].position.x>=24.9999&&horizontal[0].position.x<25.01);
 const vertical=moveWidgetsToCollisionLimit([w('m',20,70,10,10),w('b',20,20,10,.05)],['m'],0,-65);
 assert.ok(vertical[0].position.y>=20.0499&&vertical[0].position.y<20.06);
});
test('RC131: translated groups are rigid and slide boundaries still clamp',()=>{
 const items=[w('a',5,10,10,10),w('b',5,35,10,10),w('block',35,10,5,10)];
 const out=moveWidgetsToCollisionLimit(items,['a','b'],90,0);
 assert.ok(out[0].position.x>=24.99&&out[0].position.x<25.01);
 assert.equal(out[1].position.x,out[0].position.x);
 assert.equal(out[1].position.y-out[0].position.y,25);
 assert.equal(overlapsOtherWidgets(out,['a','b']),false);
 const bounded=moveWidgetsToCollisionLimit([w('a',90,90,10,10)],['a'],999,999);
 assert.equal(bounded[0].position.x,90);
 assert.equal(bounded[0].position.y,90);
});
test('RC131: free graphics retain intentional overlays while non-graphic widgets are stopped',()=>{
 const items=[w('label',12,15,9,10),w('shape',30,15,8,10,'shape'),w('block',55,15,8,10)];
 const graphic=moveWidgetsToCollisionLimit(items,['shape'],40,0);
 assert.equal(graphic[1].position.x,70);
 const text=moveWidgetsToCollisionLimit(items,['label'],70,0);
 assert.ok(text[0].position.x>=45.99&&text[0].position.x<46.01);
});
test('RC131: invalid deltas and a stale selection fail closed',()=>{
 const items=[w('label',10,10,20,10)];
 assert.equal(moveWidgetsToCollisionLimit(items,['label'],Infinity,1),items);
 assert.equal(moveWidgetsToCollisionLimit(items,['missing'],40,0),items);
});
