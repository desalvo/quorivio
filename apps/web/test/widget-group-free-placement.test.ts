import assert from 'node:assert/strict';
import test from 'node:test';
import {insertWidgetGroupInFreeSpace} from '../src/widget-selection.ts';
import {overlapsOtherWidgets} from '../src/widget-placement.ts';

const widgets=[
 {id:'a',kind:'text',position:{x:10,y:10,width:20,height:20}},
 {id:'b',kind:'text',position:{x:40,y:35,width:15,height:15}},
 {id:'c',kind:'text',position:{x:75,y:70,width:15,height:10}},
];
test('regression 40592859476: duplicates two widgets without overlapping originals',()=>{
 const r=insertWidgetGroupInFreeSpace(widgets,widgets.slice(0,2),['copy-a','copy-b']);
 assert.ok(r);assert.equal(r.widgets.length,5);
 assert.deepEqual(r.selected,['copy-a','copy-b']);
 assert.equal(overlapsOtherWidgets(r.widgets,r.selected),false);
 assert.deepEqual(r.widgets.slice(0,3),widgets);
 const [a,b]=r.widgets.slice(3);
 assert.equal(a.position.x-widgets[0].position.x,b.position.x-widgets[1].position.x);
 assert.equal(a.position.y-widgets[0].position.y,b.position.y-widgets[1].position.y);
});
test('copy/paste through the same placement preserves relative geometry',()=>{
 const source=widgets.slice(0,2).map(w=>structuredClone(w));
 const r=insertWidgetGroupInFreeSpace(widgets,source,['paste-a','paste-b'],10);
 assert.ok(r);assert.equal(r.widgets.length,5);
 assert.equal(overlapsOtherWidgets(r.widgets,r.selected),false);
});
test('the requested short offset remains preferred when genuinely free',()=>{
 const r=insertWidgetGroupInFreeSpace([widgets[0]],[widgets[0]],['copy'],5);
 assert.ok(r);assert.equal(overlapsOtherWidgets(r.widgets,r.selected),false);
});
test('a full canvas rejects group duplication without mutating existing widgets',()=>{
 const full=[{id:'full',position:{x:0,y:0,width:100,height:100}}];
 assert.equal(insertWidgetGroupInFreeSpace(full,full,['copy']),null);
 assert.deepEqual(full,[{id:'full',position:{x:0,y:0,width:100,height:100}}]);
});
test('duplicate IDs or overlapping group input never bypass safety checks',()=>{
 assert.throws(()=>insertWidgetGroupInFreeSpace(widgets,widgets.slice(0,2),['a','fresh']));
 const group=[{id:'x',position:{x:0,y:0,width:20,height:20}},{id:'y',position:{x:5,y:5,width:20,height:20}}];
 assert.equal(insertWidgetGroupInFreeSpace(group,group,['new1','new2']),null);
});
