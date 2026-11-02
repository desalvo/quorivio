import test from 'node:test';
import assert from 'node:assert/strict';
import {magneticSnapWithGuides, magneticSnapWidget, overlapsOtherWidgets, rejectWidgetCollisions} from '../src/widget-placement.ts';
const w=(id:string,x:number,y:number,width=20,height=16,kind='text')=>({id,kind,position:{x,y,width,height}});
test('RC124: align to another widget boundary, both axes, without changing width or height',()=>{
 const other=w('other',28,19,18,18);
 const c=w('c',46.9,37.4,12,10);
 const {widget,guides}=magneticSnapWithGuides(c,[other]);
 assert.equal(widget.position.x,46);
 assert.equal(widget.position.y,37);
 assert.deepEqual(guides,[{axis:'x',at:46,source:'widget'},{axis:'y',at:37,source:'widget'}]);
 assert.equal(widget.position.width,12);assert.equal(widget.position.height,10);
});
test('RC124: snap a widget center to slide center and preserve bounds',()=>{
 const c=w('c',39.2,44.7,20,10);
 const {widget,guides}=magneticSnapWithGuides(c,[]);
 assert.equal(widget.position.x,40);assert.equal(widget.position.y,45);
 assert.deepEqual(guides,[{axis:'x',at:50,source:'canvas'},{axis:'y',at:50,source:'canvas'}]);
});
test('RC124: zero or off-slide moves fail closed instead of corrupting a page',()=>{
 const c=w('c',95,50,12,10);
 const {widget,guides}=magneticSnapWithGuides(c,[w('other',96,50,2,10)]);
 assert.ok(widget.position.x<=88);
 // The source never changes during a guide calculation.
 assert.equal(c.position.x,95);
 assert.ok(guides.every(g=>g.at>=0&&g.at<=100));
});
test('RC124: malformed geometry does not generate visual guides',()=>{
 const c=w('c',39,42);c.position.x=Number.NaN;
 const {widget,guides}=magneticSnapWithGuides(c,[]);
 assert.equal(widget,c);assert.deepEqual(guides,[]);
});
test('RC124: do not mutate the input; do not persist any guide in the widget',()=>{
 const c=w('c',40.3,10,20,15);const before=structuredClone(c);
 const {widget,guides}=magneticSnapWithGuides(c,[]);
 assert.deepEqual(c,before);assert.equal('guides' in widget,false);
 assert.equal(magneticSnapWidget(c,[]).position.x,widget.position.x);
 assert.ok(guides.length>=1);
});
test('RC124: collision rule still rejects magnetic overlaps and graphic overlays stay permitted',()=>{
 const original=[w('a',5,5),w('b',50,50)];
 const proposed=[original[0],w('b',10,10)];
 assert.deepEqual(rejectWidgetCollisions(original,proposed,['b']),proposed);
 assert.ok(overlapsOtherWidgets(proposed,['b']));
 assert.equal(overlapsOtherWidgets([original[0],w('shape',10,10,18,12,'shape')],['shape']),false);
});
import {snapWidgetGroupDelta} from '../src/widget-placement.ts';
test('RC124: grid snapping uses final slide coordinates, not rounded pointer distance',()=>{
 const origin=[w('a',13,18,20,10)];
 const delta=snapWidgetGroupDelta(origin,['a'],5,5);
 assert.deepEqual(delta,{dx:7,dy:7}); // 13+7=20, 18+7=25
});
test('RC124: multi-selection grid uses common bounding box and preserves relative geometry',()=>{
 const origin=[w('a',13,18),w('b',44,36)];
 const delta=snapWidgetGroupDelta(origin,['a','b'],4,4);
 assert.deepEqual(delta,{dx:2,dy:2});
 const left=origin[0].position.x+delta.dx,right=origin[1].position.x+delta.dx;
 assert.equal(left,15);assert.equal(right-left,31);
});
test('RC124: grid movement remains bounded and nonselected widgets do not affect snap',()=>{
 const origin=[w('a',79,83,20,16),w('b',3,4,5,5)];
 const delta=snapWidgetGroupDelta(origin,['a'],50,50);
 assert.deepEqual(delta,{dx:1,dy:1});
 assert.deepEqual(snapWidgetGroupDelta(origin,[],5,5),{dx:0,dy:0});
 assert.deepEqual(snapWidgetGroupDelta(origin,['a'],Number.NaN,5),{dx:0,dy:0});
});
