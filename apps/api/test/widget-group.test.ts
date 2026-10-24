import test from 'node:test';
import assert from 'node:assert/strict';
import {moveWidgetGroup,pasteWidgetGroup,widgetRect} from '../../web/src/widget-group.ts';
const original=[{id:'a',position:{x:10,y:20,width:20,height:20}},{id:'b',position:{x:60,y:40,width:30,height:30}},{id:'c',position:{x:0,y:0,width:10,height:10}}];
test('group move preserves relative offsets and leaves unselected objects unchanged',()=>{
 const moved=moveWidgetGroup(original,['a','b'],5,-10);
 assert.deepEqual(moved.slice(0,2).map(w=>[w.position.x,w.position.y]),[[15,10],[65,30]]);
 assert.equal(moved[2],original[2]);assert.deepEqual(original[0].position,{x:10,y:20,width:20,height:20});
});
test('group move clamps to rightmost widget and bottommost widget together',()=>{
 const moved=moveWidgetGroup(original,['a','b'],30,90);
 assert.deepEqual(moved.slice(0,2).map(w=>[w.position.x,w.position.y]),[[20,50],[70,70]]);
});
test('group move clamps negative delta against leftmost and topmost',()=>{
 const moved=moveWidgetGroup(original,['a','b'],-40,-40);
 assert.deepEqual(moved.slice(0,2).map(w=>[w.position.x,w.position.y]),[[0,0],[50,20]]);
});
test('group move ignores unknown selection, empty selection and invalid delta',()=>{
 assert.equal(moveWidgetGroup(original,['missing'],10,10),original);
 assert.equal(moveWidgetGroup(original,[],10,10),original);
 assert.equal(moveWidgetGroup(original,['a'],Infinity,1),original);
});
test('group paste clones content with new identities and stable relative positions',()=>{
 const pasted=pasteWidgetGroup(original.slice(0,2),['new-a','new-b']);
 assert.deepEqual(pasted.map(w=>w.id),['new-a','new-b']);
 assert.deepEqual(pasted.map(w=>[w.position.x,w.position.y]),[[15,25],[65,45]]);
 pasted[0].position.x=50;assert.equal(original[0].position.x,10);
});
test('group paste clamps offset globally to preserve arrangement',()=>{
 const pasted=pasteWidgetGroup(original.slice(0,2),['new-a','new-b'],20);
 assert.deepEqual(pasted.map(w=>w.position.x),[20,70]);
 assert.deepEqual(pasted.map(w=>w.position.y),[40,60]);
});
test('group paste rejects duplicate, original and missing identities',()=>{
 assert.throws(()=>pasteWidgetGroup(original,['same','same','third']));
 assert.throws(()=>pasteWidgetGroup(original,['a','new-b','new-c']));
 assert.throws(()=>pasteWidgetGroup(original,['new-a']));
 assert.throws(()=>pasteWidgetGroup(original,['new-a','new-b','new-c'],NaN));
});
test('invalid imported geometry is normalized to canvas before group operations',()=>{
 assert.deepEqual(widgetRect({id:'a',position:{x:999,y:-9,width:150,height:0}}),{x:0,y:0,width:100,height:.01,rotation:0});
});
