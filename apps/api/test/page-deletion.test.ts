import test from 'node:test';
import assert from 'node:assert/strict';
import {unlinkDeletedPage} from '../src/page-deletion.ts';

const deleted='a0a0a0a0-0000-4000-8000-000000000001';
test('confirmed deletion detaches audience and source links without deleting other page content',()=>{
 const original={audiencePageId:deleted,presenterHidden:true,header:'Da conservare',widgets:[
  {id:'result',kind:'results-button',targetActivityId:deleted,targetWidgetId:'source',targetQuestionId:'q',showSourceQuestion:true},
  {id:'local',kind:'results-button',targetWidgetId:'same-page'},
  {id:'title',kind:'title',label:'Pagina'}
 ]};
 const r=unlinkDeletedPage(original,deleted);
 assert.equal(r.changed,true);
 const out=r.design as typeof original;
 assert.equal('audiencePageId' in out,false);
 assert.equal(out.presenterHidden,true);assert.equal(out.header,'Da conservare');
 assert.deepEqual(out.widgets[0],{id:'result',kind:'results-button',showSourceQuestion:true});
 assert.deepEqual(out.widgets[1],original.widgets[1]);
 assert.deepEqual(out.widgets[2],original.widgets[2]);
 assert.equal(original.widgets[0].targetActivityId,deleted,'do not modify snapshot');
 assert.equal(original.audiencePageId,deleted,'do not mutate saved source');
});
test('delete only matching page references including historical result design',()=>{
 const other='a0a0a0a0-0000-4000-8000-000000000002';
 const original={widgets:[{id:'x',kind:'results-button',targetActivityId:other,targetWidgetId:'w'}]};
 assert.equal(unlinkDeletedPage(original,deleted).changed,false);
 assert.equal(unlinkDeletedPage(original,deleted).design,original);
 const response=unlinkDeletedPage({widgets:[{id:'legacy',kind:'results-button',targetActivityId:deleted,targetWidgetId:'w'}]},deleted);
 assert.equal(response.changed,true);
 assert.deepEqual((response.design as any).widgets,[{id:'legacy',kind:'results-button'}]);
});
test('empty, malformed and missing designs cannot create dangling route changes',()=>{
 for(const value of [null,undefined,[],false,3])assert.equal(unlinkDeletedPage(value,deleted).changed,false);
});
