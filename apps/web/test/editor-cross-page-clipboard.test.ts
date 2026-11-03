import test from 'node:test';
import assert from 'node:assert/strict';
import {saveEditorWidgetClipboard,readEditorWidgetClipboard,clearEditorWidgetClipboard} from '../src/editor-cross-page-clipboard.ts';
import {insertWidgetGroupInFreeSpace} from '../src/widget-selection.ts';

test('RC142: widget copy survives page switch within the same session and assigns fresh IDs',()=>{
 const original=[{id:'question1',kind:'question',label:'Question A',position:{x:8,y:6,width:30,height:20}},{id:'result1',kind:'results-button',targetWidgetId:'question1',position:{x:55,y:10,width:24,height:18}}];
 assert.equal(saveEditorWidgetClipboard('session1',original),2);
 original[0].label='Modified after copy';
 const fetched=readEditorWidgetClipboard('session1');
 assert.equal(fetched[0].label,'Question A');
 assert.deepEqual(readEditorWidgetClipboard('other-session'),[]);
 const pasted=insertWidgetGroupInFreeSpace([],fetched,['newQ','newR'],5);
 assert.ok(pasted);assert.equal(pasted!.selected.length,2);
 assert.equal((pasted!.widgets[1] as any).targetWidgetId,'newQ');
 clearEditorWidgetClipboard();assert.deepEqual(readEditorWidgetClipboard('session1'),[]);
});

test('RC142: widget clipboard does not persist an empty or unscoped selection',()=>{
 assert.equal(saveEditorWidgetClipboard('',[{id:'a'}]),0);
 assert.equal(saveEditorWidgetClipboard('s',[]),0);
 assert.deepEqual(readEditorWidgetClipboard('other'),[]);
});
