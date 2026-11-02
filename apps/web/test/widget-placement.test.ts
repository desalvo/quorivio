import assert from 'node:assert/strict';
import test from 'node:test';
import {overlapsOtherWidgets,rejectWidgetCollisions,magneticSnapWidget,freeWidgetPosition} from '../src/widget-placement.ts';
const a={id:'a',position:{x:10,y:10,width:20,height:20}};
const b={id:'b',position:{x:30,y:10,width:20,height:20}};
test('touching borders are not reported as overlaps',()=>{assert.equal(overlapsOtherWidgets([a,b],['a']),false)});
test('RC138: intersecting widget positions are persisted intentionally',()=>{
 const crossed=[a,{...b,position:{...b.position,x:25}}];
 assert.equal(overlapsOtherWidgets(crossed,['b']),true);
 assert.deepEqual(rejectWidgetCollisions([a,b],crossed,['b']),crossed);
});
test('magnetic edge placement uses stable percentage boundaries',()=>{
 const candidate={id:'c',position:{x:50.8,y:10.9,width:16,height:10}};
 const snapped=magneticSnapWidget(candidate,[b],1.5);
 assert.equal(snapped.position.x,50);assert.equal(snapped.position.y,10);
});
test('RC138: new widget keeps its desired drop point even when another fills it',()=>{
 const slot=freeWidgetPosition([a],{x:11,y:11},20,20);assert.deepEqual(slot,{x:11,y:11,width:20,height:20});
 assert.equal(overlapsOtherWidgets([a,{id:'c',position:slot!}],['c']),true);
 assert.deepEqual(freeWidgetPosition([{id:'wide',position:{x:0,y:0,width:100,height:100}}],{x:0,y:0},20,20),{x:0,y:0,width:20,height:20});
 assert.equal(freeWidgetPosition([],{x:0,y:0},120,20),null);
});
