import test from 'node:test';
import assert from 'node:assert/strict';
import {newWidgetHistory,editWidgets,beginWidgetGesture,endWidgetGesture,undoWidgets,redoWidgets,MAX_WIDGET_UNDO} from '../../web/src/widget-history.ts';
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
