import test from 'node:test';import assert from 'node:assert/strict';import {pasteWidgetGroup} from '../src/widget-group.ts';
test('duplicating a linked result and its source preserves their internal cloned reference',()=>{
 const original=[{id:'q1',kind:'question',position:{x:5,y:5,width:15,height:15}},{id:'r1',kind:'results-button',targetWidgetId:'q1',position:{x:25,y:5,width:15,height:15}}];
 const copies=pasteWidgetGroup(original,['q2','r2'],20);
 assert.equal(copies[1].targetWidgetId,'q2');assert.equal(original[1].targetWidgetId,'q1');
});
test('copying only the result preserves its reference to the existing page source',()=>{
 const copied=pasteWidgetGroup([{id:'r1',kind:'results-button',targetWidgetId:'q1',position:{x:20,y:20,width:10,height:10}}],['r2']);
 assert.equal(copied[0].targetWidgetId,'q1');
});
