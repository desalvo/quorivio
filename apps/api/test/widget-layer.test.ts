import test from 'node:test';
import assert from 'node:assert/strict';
import {reorderWidgetLayers} from '../../web/src/widget-layer.ts';
const widgets=['a','b','c','d','e','f'].map(id=>({id,meta:{id}}));
const ids=(w:typeof widgets)=>w.map(x=>x.id);
test('move a disjoint selection to front in stable relative order',()=>{
 assert.deepEqual(ids(reorderWidgetLayers(widgets,['b','d'],'front')),['a','c','e','f','b','d']);
});
test('move disjoint selection to back in stable relative order',()=>{
 assert.deepEqual(ids(reorderWidgetLayers(widgets,['d','b'],'back')),['b','d','a','c','e','f']);
});
test('move disjoint selection forward exactly one layer per item',()=>{
 assert.deepEqual(ids(reorderWidgetLayers(widgets,['b','d'],'forward')),['a','c','b','e','d','f']);
});
test('move disjoint selection backward exactly one layer per item',()=>{
 assert.deepEqual(ids(reorderWidgetLayers(widgets,['b','d'],'backward')),['b','a','d','c','e','f']);
});
test('consecutive selection moves as a block when advancing',()=>{
 assert.deepEqual(ids(reorderWidgetLayers(widgets,['b','c'],'forward')),['a','d','b','c','e','f']);
});
test('consecutive selection moves as a block when retreating',()=>{
 assert.deepEqual(ids(reorderWidgetLayers(widgets,['b','c'],'backward')),['b','c','a','d','e','f']);
});
test('already-front and already-back selections are identity no-ops',()=>{
 assert.equal(reorderWidgetLayers(widgets,['e','f'],'front'),widgets);
 assert.equal(reorderWidgetLayers(widgets,['a','b'],'back'),widgets);
});
test('unknown/empty IDs do not reorder, nor mutate input',()=>{
 assert.equal(reorderWidgetLayers(widgets,['unknown'],'front'),widgets);
 assert.equal(reorderWidgetLayers(widgets,[],'forward'),widgets);
 assert.deepEqual(ids(widgets),['a','b','c','d','e','f']);
});
test('reordering retains the exact original widget objects and metadata',()=>{
 const out=reorderWidgetLayers(widgets,['a','c'],'front');
 assert.equal(out[4],widgets[0]);assert.equal(out[5],widgets[2]);
});
