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
test('horizontal equal gaps use widget edges rather than unequal centers',()=>{
 const result=run('space-x').slice(0,3).map(w=>w.position);
 const ordered=[...result].sort((a,b)=>a.x-b.x);
 const gaps=[ordered[1].x-(ordered[0].x+ordered[0].width),ordered[2].x-(ordered[1].x+ordered[1].width)];
 assert.ok(Math.abs(gaps[0]-gaps[1])<.0002,gaps.join(','));
});
test('vertical equal gaps use widget edges',()=>{
 const result=run('space-y').slice(0,3).map(w=>w.position);
 const ordered=[...result].sort((a,b)=>a.y-b.y);
 const gaps=[ordered[1].y-(ordered[0].y+ordered[0].height),ordered[2].y-(ordered[1].y+ordered[1].height)];
 assert.ok(Math.abs(gaps[0]-gaps[1])<.0002,gaps.join(','));
});
test('horizontal group canvas centering preserves relative x spacing',()=>{
 const result=run('canvas-center-x');const rects=result.slice(0,3).map(w=>w.position);
 const left=Math.min(...rects.map(p=>p.x)),right=Math.max(...rects.map(p=>p.x+p.width));
 assert.ok(Math.abs((left+right)/2-50)<.0001);
 assert.ok(Math.abs((rects[1].x-rects[0].x)-35)<.0001);
});
test('vertical group canvas centering preserves relative y spacing',()=>{
 const result=run('canvas-center-y');const rects=result.slice(0,3).map(w=>w.position);
 const top=Math.min(...rects.map(p=>p.y)),bottom=Math.max(...rects.map(p=>p.y+p.height));
 assert.ok(Math.abs((top+bottom)/2-50)<.0001);
 assert.ok(Math.abs((rects[1].y-rects[0].y)-25)<.0001);
});
test('single widget can be centered on either canvas axis',()=>{
 const x=arrangeWidgets(widgets,['a'],'canvas-center-x');
 const y=arrangeWidgets(widgets,['a'],'canvas-center-y');
 assert.equal(x[0].position.x,40);assert.equal(y[0].position.y,40);
});
test('equal-gap distribution requires three widgets and is a no-op for two',()=>{
 assert.equal(arrangeWidgets(widgets,['a','b'],'space-x'),widgets);
 assert.equal(arrangeWidgets(widgets,['a','b'],'space-y'),widgets);
});
test('canvas centering leaves all unselected widgets unchanged',()=>{
 assert.equal(run('canvas-center-x')[3],widgets[3]);
 assert.equal(run('canvas-center-y')[3],widgets[3]);
});
