import test from 'node:test';
import assert from 'node:assert/strict';
import {newWidgetHistory,editWidgets,reconcileWidgetAutoFit,beginWidgetGesture,endWidgetGesture,undoWidgets,redoWidgets,MAX_WIDGET_UNDO} from '../../web/src/widget-history.ts';
const a = [{id:'a',x:0}];
const b = [{id:'a',x:5}];
test('widget edits undo, redo and invalidate redo on divergent edit',()=>{
 let h=newWidgetHistory(a);
 h=editWidgets(h,b);assert.deepEqual(h.past,[a]);
 h=undoWidgets(h);assert.deepEqual(h.present,a);
 h=redoWidgets(h);assert.deepEqual(h.present,b);
 h=undoWidgets(h);h=editWidgets(h,[{id:'b',x:1}]);assert.equal(h.future.length,0);
});
test('a pointer gesture groups all intermediate positions into one undo',()=>{
 let h=beginWidgetGesture(newWidgetHistory(a));
 for(let x=1;x<=20;x++)h=editWidgets(h,[{id:'a',x}]);
 assert.equal(h.past.length,0);
 h=endWidgetGesture(h);assert.equal(h.past.length,1);
 h=undoWidgets(h);assert.deepEqual(h.present,a);
});
test('cancelled gesture does not add history',()=>{
 let h=beginWidgetGesture(newWidgetHistory(a));h=editWidgets(h,b);h=editWidgets(h,a);h=endWidgetGesture(h);
 assert.equal(h.past.length,0);
});
test('page reset does not leak previous page undo stack',()=>{
 const edited=editWidgets(newWidgetHistory(a),b);
 assert.equal(edited.past.length,1);
 const other=newWidgetHistory([{id:'other',x:3}]);assert.equal(other.past.length,0);
});
test('history is bounded and idempotent',()=>{
 let h=newWidgetHistory(a);
 h=editWidgets(h,a);assert.equal(h.past.length,0);
 for(let x=1;x<MAX_WIDGET_UNDO+20;x++)h=editWidgets(h,[{id:'a',x}]);
 assert.equal(h.past.length,MAX_WIDGET_UNDO);
});
test('undo is disabled mid gesture and redo cannot run mid gesture',()=>{
 let h=editWidgets(newWidgetHistory(a),b);h=beginWidgetGesture(h);
 assert.equal(undoWidgets(h),h);assert.equal(redoWidgets(h),h);
});

test('auto-fit following group duplication does not consume a second undo slot',()=>{
 const initial=[{id:'a',position:{height:10}},{id:'b',position:{height:12}},{id:'c',position:{height:11}}];
 const duplicated=[...initial,{id:'a-copy',position:{height:10}},{id:'b-copy',position:{height:12}}];
 let state=editWidgets(newWidgetHistory(initial),duplicated);
 const fitted=duplicated.map(w=>w.id==='a-copy'?{...w,position:{height:20}}:w);
 state=reconcileWidgetAutoFit(state,duplicated,fitted);
 assert.equal(state.past.length,1);assert.deepEqual(state.present,fitted);
 state=undoWidgets(state);assert.deepEqual(state.present,initial);
 state=redoWidgets(state);assert.deepEqual(state.present,fitted);
});
test('auto-fit does not override stale, reordered or in-progress history',()=>{
 const initial=[{id:'a',position:{height:10}}];
 const next=[{id:'a',position:{height:15}}];
 const further=[{id:'a',position:{height:20}}];
 let state=editWidgets(newWidgetHistory(initial),next);
 const stale=state;state=editWidgets(state,further);
 assert.equal(reconcileWidgetAutoFit(state,next,initial),state,'stale effect');
 assert.equal(reconcileWidgetAutoFit(state,further,[{id:'other',position:{height:24}}]),state,'different widget identity');
 state=beginWidgetGesture(state);
 assert.equal(reconcileWidgetAutoFit(state,further,next),state,'pointer gesture in progress');
 assert.notDeepEqual(reconcileWidgetAutoFit(stale,next,further),stale,'valid current derived change');
});
