import test from 'node:test';
import assert from 'node:assert/strict';
import {arrangeWidgets} from '../../web/src/widget-arrange.ts';
const widgets=[
 {id:'a',position:{x:10,y:10,width:20,height:20}},
 {id:'b',position:{x:45,y:35,width:10,height:15}},
 {id:'c',position:{x:75,y:70,width:15,height:10}},
 {id:'unselected',position:{x:2,y:3,width:4,height:5}}
];
const ids=['a','b','c'];
const run=(mode:Parameters<typeof arrangeWidgets>[2])=>arrangeWidgets(widgets,ids,mode);
const p=(items:typeof widgets[],i:number)=>items[i];
test('left/right align three selected widgets without touching others',()=>{
 const left=run('left');assert.deepEqual(left.slice(0,3).map(w=>w.position.x),[10,10,10]);assert.equal(left[3],widgets[3]);
 const right=run('right');assert.deepEqual(right.slice(0,3).map(w=>w.position.x+w.position.width),[90,90,90]);
});
test('top/bottom align preserves dimensions',()=>{
 assert.deepEqual(run('top').slice(0,3).map(w=>w.position.y),[10,10,10]);
 assert.deepEqual(run('bottom').slice(0,3).map(w=>w.position.y+w.position.height),[80,80,80]);
});
test('centers align on shared bounding box',()=>{
 const x=run('center-x').slice(0,3).map(w=>w.position.x+w.position.width/2);
 const y=run('center-y').slice(0,3).map(w=>w.position.y+w.position.height/2);
 assert.ok(x.every(v=>v===50));assert.ok(y.every(v=>v===45));
});
test('equal size takes first selected widget as reference',()=>{
 assert.deepEqual(run('same-width').slice(0,3).map(w=>w.position.width),[20,20,20]);
 assert.deepEqual(run('same-height').slice(0,3).map(w=>w.position.height),[20,20,20]);
});
test('distribution evenly spaces centers in x and y',()=>{
 const x=run('distribute-x').slice(0,3).map(w=>w.position.x+w.position.width/2);
 const y=run('distribute-y').slice(0,3).map(w=>w.position.y+w.position.height/2);
 assert.ok(Math.abs(x[1]-(x[0]+x[2])/2)<.0001);
 assert.ok(Math.abs(y[1]-(y[0]+y[2])/2)<.0001);
});
test('less than two selections is a no-op and never mutates',()=>{
 assert.equal(arrangeWidgets(widgets,['a'],'left'),widgets);
 assert.deepEqual(widgets[0].position,{x:10,y:10,width:20,height:20});
});
test('invalid or missing positions are clamped to canvas bounds',()=>{
 const result=arrangeWidgets([{id:'a',position:{x:98,y:99,width:80,height:90}},{id:'b',position:{x:-3,y:-4,width:10,height:10}}],['a','b'],'left');
 for(const w of result){const r=w.position!;assert.ok(r.x>=0&&r.y>=0&&r.x+r.width<=100&&r.y+r.height<=100)}
});
test('distribute equal centers deterministically, preserve stable ID order',()=>{
 const same=[{id:'z',position:{x:20,y:20,width:10,height:10}},{id:'a',position:{x:20,y:20,width:10,height:10}},{id:'m',position:{x:20,y:20,width:10,height:10}}];
 assert.deepEqual(arrangeWidgets(same,['z','a','m'],'distribute-x'),same);
});
