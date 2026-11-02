import test from 'node:test';
import assert from 'node:assert/strict';
import {resizeWidgetToCollisionLimit,overlapsOtherWidgets} from '../src/widget-placement.ts';
import {newWidgetHistory,beginWidgetGesture,editWidgets,endWidgetGesture,undoWidgets,redoWidgets} from '../src/widget-history.ts';
const w=(id:string,x:number,y:number,width:number,height:number,kind='question')=>({id,kind,position:{x,y,width,height,rotation:0},autoFit:true});

test('RC133 east resize stops at thin barrier even after huge pointer jump',()=>{
 const original=[w('selected',10,10,10,12),w('barrier',28.05,9,.05,14)];
 const next=resizeWidgetToCollisionLimit(original,'selected',{x:10,y:10,width:70,height:12});
 assert.ok(next[0].position.width>17.99&&next[0].position.width<=18.05,JSON.stringify(next));
 assert.equal(overlapsOtherWidgets(next,['selected']),false);
 assert.equal(original[0].position.width,10);
});
test('RC133 west and north resize clamp at neighbours with fixed opposite edges',()=>{
 const original=[w('a',40,40,20,20),w('west',29,40,1,20),w('north',40,28,20,2)];
 const left=resizeWidgetToCollisionLimit(original,'a',{x:5,y:40,width:55,height:20});
 assert.ok(left[0].position.x>=29.99&&left[0].position.x<=30.01);
 assert.ok(Math.abs(left[0].position.x+left[0].position.width-60)<.001);
 const up=resizeWidgetToCollisionLimit(original,'a',{x:40,y:0,width:20,height:60});
 assert.ok(up[0].position.y>=29.99&&up[0].position.y<=30.01);
 assert.ok(Math.abs(up[0].position.y+up[0].position.height-60)<.001);
});
test('RC133 diagonal resize stops at first obstruction and never moves opposite edges',()=>{
 const original=[w('a',10,10,10,10),w('east',34,10,2,50),w('south',10,39,40,2)];
 const next=resizeWidgetToCollisionLimit(original,'a',{x:10,y:10,width:70,height:70});
 assert.equal(next[0].position.x,10);
 assert.equal(next[0].position.y,10);
 assert.ok(next[0].position.width>23&&next[0].position.width<=24.01);
 assert.equal(overlapsOtherWidgets(next,['a']),false);
});
test('RC133 shrinking never bounces, shape/line may overlay, and other widgets stay immutable',()=>{
 const original=[w('a',10,10,30,20),w('b',50,10,5,20)];
 const small=resizeWidgetToCollisionLimit(original,'a',{x:10,y:10,width:5,height:10});
 assert.deepEqual(small[0].position,{x:10,y:10,width:5,height:10,rotation:0});
 assert.equal(small[1],original[1]);
 const shape=[w('shape',10,10,10,10,'shape'),w('b',25,10,5,10)];
 assert.equal(resizeWidgetToCollisionLimit(shape,'shape',{x:10,y:10,width:50,height:10})[0].position.width,50);
});
test('RC133 malformed, out-of-canvas and originally overlapping resizes are rejected',()=>{
 const original=[w('a',20,20,10,10),w('b',40,20,10,10)];
 for(const p of [
  {x:20,y:20,width:Infinity,height:10},
  {x:-1,y:20,width:10,height:10},
  {x:20,y:20,width:90,height:10},
  {x:20,y:20,width:0,height:10},
 ])assert.deepEqual(resizeWidgetToCollisionLimit(original,'a',p),original);
 assert.deepEqual(resizeWidgetToCollisionLimit([w('a',10,10,15,10),w('b',20,10,10,10)],'a',{x:10,y:10,width:22,height:10})[0].position,{x:10,y:10,width:15,height:10,rotation:0});
});
test('RC133 repeated pointer positions do not collapse, group remains untouched',()=>{
 const base=[w('a',10,10,10,10),w('wall',30,10,5,10)];
 const first=resizeWidgetToCollisionLimit(base,'a',{x:10,y:10,width:60,height:10});
 const second=resizeWidgetToCollisionLimit(base,'a',{x:10,y:10,width:60,height:10});
 assert.deepEqual(first,second);
});
test('RC133 entire pointer resize forms a single reversible undo transaction',()=>{
 const base=[w('a',10,10,10,10),w('wall',40,10,5,10)];
 let h=newWidgetHistory(base);h=beginWidgetGesture(h);
 h=editWidgets(h,resizeWidgetToCollisionLimit(base,'a',{x:10,y:10,width:20,height:10}));
 h=editWidgets(h,resizeWidgetToCollisionLimit(base,'a',{x:10,y:10,width:70,height:10}));
 h=endWidgetGesture(h);
 assert.equal(h.past.length,1);
 const saved=h.present;
 h=undoWidgets(h);assert.deepEqual(h.present,base);
 h=redoWidgets(h);assert.deepEqual(h.present,saved);
});
