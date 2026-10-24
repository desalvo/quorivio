import test from 'node:test';
import assert from 'node:assert/strict';
import {existingWidgetIds,deleteWidgetSelection,duplicateWidgetSelection,nudgeWidgetSelection} from '../../web/src/widget-selection.ts';
const widgets=[
 {id:'a',kind:'text',position:{x:10,y:10,width:20,height:20},style:{color:'blue'}},
 {id:'b',kind:'text',position:{x:60,y:60,width:20,height:20},style:{color:'red'}},
 {id:'c',kind:'image',position:{x:90,y:90,width:10,height:10},style:{color:'green'}}
];
test('selection filters orphan IDs and deduplicates in requested order',()=>{
 assert.deepEqual(existingWidgetIds(widgets,['missing','b','b','a']),['b','a']);
});
test('deleting a multi-selection preserves unselected identity',()=>{
 const out=deleteWidgetSelection(widgets,['a','c']);assert.deepEqual(out.map(w=>w.id),['b']);assert.equal(out[0],widgets[1]);
});
test('deleting nonexistent selection is a reference no-op',()=>{
 assert.equal(deleteWidgetSelection(widgets,['unknown']),widgets);
});
test('duplicating selected widgets preserves document layer order and clones nested style',()=>{
 const out=duplicateWidgetSelection(widgets,['b','a'],['a2','b2']);
 assert.deepEqual(out.selected,['a2','b2']);assert.deepEqual(out.widgets.map(w=>w.id),['a','b','c','a2','b2']);
 assert.notEqual(out.widgets[3].style,widgets[0].style);
 out.widgets[3].style.color='purple';assert.equal(widgets[0].style.color,'blue');
});
test('duplicate IDs cannot collide with existing nonselected widgets',()=>{
 assert.throws(()=>duplicateWidgetSelection(widgets,['a'],['c']),/conflicts/);
});
test('duplicate IDs must be unique and complete',()=>{
 assert.throws(()=>duplicateWidgetSelection(widgets,['a','b'],['z','z']));
 assert.throws(()=>duplicateWidgetSelection(widgets,['a','b'],['z']));
});
test('duplicating empty selection never changes document',()=>{
 const out=duplicateWidgetSelection(widgets,['unknown'],[]);assert.equal(out.widgets,widgets);assert.deepEqual(out.selected,[]);
});
test('nudge translates entire group without changing relative spacing',()=>{
 const out=nudgeWidgetSelection(widgets,['a','b'],3,-5);
 assert.deepEqual(out.slice(0,2).map(w=>[w.position.x,w.position.y]),[[13,5],[63,55]]);
 assert.equal(out[2],widgets[2]);
});
test('nudge is clamped globally at canvas edge',()=>{
 const out=nudgeWidgetSelection(widgets,['a','c'],100,100);
 assert.deepEqual(out.slice(0,1).map(w=>[w.position.x,w.position.y]),[[10,10]]);
 assert.equal(out[2],widgets[2]);
});
test('nudge rejects nonfinite displacement without mutation',()=>{
 assert.equal(nudgeWidgetSelection(widgets,['a'],Infinity,1),widgets);
});
