import assert from 'node:assert/strict';
import test from 'node:test';
import {insertWidgetGroupInFreeSpace} from '../src/widget-selection.ts';
import {overlapsOtherWidgets} from '../src/widget-placement.ts';
const widgets=[
 {id:'a',kind:'text',position:{x:10,y:10,width:20,height:20}},
 {id:'b',kind:'text',position:{x:40,y:35,width:15,height:15}},
 {id:'c',kind:'text',position:{x:75,y:70,width:15,height:10}},
];
test('RC138: duplicate groups preserve geometry even when originals overlap',()=>{
 const r=insertWidgetGroupInFreeSpace(widgets,widgets.slice(0,2),['copy-a','copy-b']);
 assert.ok(r);assert.equal(r.widgets.length,5);assert.deepEqual(r.selected,['copy-a','copy-b']);
 assert.equal(r.widgets[3].position.x,15);assert.equal(r.widgets[4].position.x,45);
 assert.deepEqual(r.widgets.slice(0,3),widgets);
});
test('RC138: copy/paste preserves relative offsets',()=>{
 const r=insertWidgetGroupInFreeSpace(widgets,widgets.slice(0,2),['paste-a','paste-b'],10);
 assert.ok(r);assert.equal(r.widgets[3].position.x,20);assert.equal(r.widgets[4].position.x,50);
});
test('RC138: a full canvas permits another overlapping copy without extending bounds',()=>{
 const full=[{id:'full',position:{x:0,y:0,width:100,height:100}}];
 const r=insertWidgetGroupInFreeSpace(full,full,['copy']);
 assert.ok(r);assert.deepEqual(r.widgets[1].position,{x:0,y:0,width:100,height:100});
 assert.equal(overlapsOtherWidgets(r.widgets,['copy']),true);
});
test('RC138: invalid duplicate ID is rejected while an overlapping selected group is supported',()=>{
 assert.throws(()=>insertWidgetGroupInFreeSpace(widgets,widgets.slice(0,2),['a','fresh']));
 const group=[{id:'x',position:{x:0,y:0,width:20,height:20}},{id:'y',position:{x:5,y:5,width:20,height:20}}];
 const result=insertWidgetGroupInFreeSpace(group,group,['new1','new2']);
 assert.ok(result);assert.equal(result.selected.length,2);
});
