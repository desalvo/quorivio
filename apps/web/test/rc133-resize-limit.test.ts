import test from 'node:test';
import assert from 'node:assert/strict';
import {resizeWidgetToCollisionLimit,overlapsOtherWidgets} from '../src/widget-placement.ts';
import {newWidgetHistory,beginWidgetGesture,editWidgets,endWidgetGesture,undoWidgets,redoWidgets} from '../src/widget-history.ts';
const w=(id:string,x:number,y:number,width:number,height:number,kind='question')=>({id,kind,position:{x,y,width,height,rotation:0},autoFit:true});
test('RC138: east resizing can overlap arbitrarily thin neighbours',()=>{
 const original=[w('selected',10,10,10,12),w('barrier',28.05,9,.05,14)];
 const next=resizeWidgetToCollisionLimit(original,'selected',{x:10,y:10,width:70,height:12});
 assert.equal(next[0].position.width,70);assert.equal(overlapsOtherWidgets(next,['selected']),true);
 assert.equal(next[0].autoFit,true);assert.equal(original[0].autoFit,true);
});
test('RC138: west/north resizing can reach the canvas border through widgets',()=>{
 const original=[w('a',40,40,20,20),w('west',29,40,1,20),w('north',40,28,20,2)];
 const left=resizeWidgetToCollisionLimit(original,'a',{x:5,y:40,width:55,height:20});
 assert.equal(left[0].position.x,5);assert.equal(left[0].position.width,55);
 const up=resizeWidgetToCollisionLimit(original,'a',{x:40,y:0,width:20,height:60});
 assert.equal(up[0].position.y,0);assert.equal(up[0].position.height,60);
});
test('RC138: diagonal resize preserves opposing anchored edges',()=>{
 const original=[w('a',10,10,10,10),w('east',34,10,2,50),w('south',10,39,40,2)];
 const next=resizeWidgetToCollisionLimit(original,'a',{x:10,y:10,width:70,height:70});
 assert.deepEqual(next[0].position,{x:10,y:10,width:70,height:70,rotation:0});
});
test('RC138: shrink never bounces, and other widgets remain immutable',()=>{
 const original=[w('a',10,10,30,20),w('b',50,10,5,20)];
 const next=resizeWidgetToCollisionLimit(original,'a',{x:10,y:10,width:5,height:10});
 assert.equal(next[0].position.width,5);assert.equal(next[1],original[1]);
});
test('RC138: malformed and out-of-canvas boxes rejected, preexisting overlays accepted',()=>{
 const original=[w('a',20,20,10,10),w('b',40,20,10,10)];
 for(const p of [{x:20,y:20,width:Infinity,height:10},{x:-1,y:20,width:10,height:10},
  {x:20,y:20,width:90,height:10},{x:20,y:20,width:0,height:10}])
  assert.deepEqual(resizeWidgetToCollisionLimit(original,'a',p),original);
 assert.equal(resizeWidgetToCollisionLimit([w('a',10,10,15,10),w('b',20,10,10,10)],'a',{x:10,y:10,width:22,height:10})[0].position.width,22);
});
test('RC138: repeated pointer targets produce stable geometry',()=>{
 const base=[w('a',10,10,10,10),w('wall',30,10,5,10)];
 assert.deepEqual(resizeWidgetToCollisionLimit(base,'a',{x:10,y:10,width:60,height:10}),resizeWidgetToCollisionLimit(base,'a',{x:10,y:10,width:60,height:10}));
});
test('RC138: manual resizing is one reversible undo/redo transaction',()=>{
 const base=[w('a',10,10,10,10),w('wall',40,10,5,10)];
 let h=newWidgetHistory(base);h=beginWidgetGesture(h);
 h=editWidgets(h,resizeWidgetToCollisionLimit(base,'a',{x:10,y:10,width:20,height:10}));
 h=editWidgets(h,resizeWidgetToCollisionLimit(base,'a',{x:10,y:10,width:70,height:10}));
 h=endWidgetGesture(h);assert.equal(h.past.length,1);
 const saved=h.present;h=undoWidgets(h);assert.deepEqual(h.present,base);
 h=redoWidgets(h);assert.deepEqual(h.present,saved);
});
