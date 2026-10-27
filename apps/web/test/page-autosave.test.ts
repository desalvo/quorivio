import test from 'node:test';
import assert from 'node:assert/strict';
import {autosaveRecoveryDecision,recoverableAutosaveTransportError,retryAutosaveDelay} from '../src/page-autosave.ts';
import {type EditablePageDraft} from '../src/page-draft.ts';
const draft:EditablePageDraft={widgets:[{id:'e8118c4f-aeb5-44d6-b03a-bf952b6bc170',kind:'text',label:'New',position:{x:10,y:20,width:35,height:15,rotation:0}}],questionHeader:'Header',resultHeader:'Results',questionBackground:'',resultBackground:'',questionBackgroundColor:'',resultBackgroundColor:'',questionBackgroundAsset:'',resultBackgroundAsset:''};
const remote=(version:number, widgets=draft.widgets)=>({design_revision:version,page_design:{widgets,header:'Header'},result_design:{header:'Results'}});
test('uncertain lost PATCH response is reconciled with server before retry',()=>{
 assert.equal(autosaveRecoveryDecision(remote(3),draft,2),'persisted');
 assert.equal(autosaveRecoveryDecision(remote(3),draft,2,3),'persisted');
 assert.equal(autosaveRecoveryDecision(remote(2,[{id:'other'}]),draft,2),'unchanged');
});
test('never interpret another presenter write as successful local autosave',()=>{
 assert.equal(autosaveRecoveryDecision(remote(3,[{id:'other'}]),draft,2),'conflict');
 assert.equal(autosaveRecoveryDecision(remote(4),draft,2),'conflict');
 assert.equal(autosaveRecoveryDecision(undefined,draft,2),'unverifiable');
 assert.equal(autosaveRecoveryDecision({design_revision:'3'},draft,2),'unverifiable');
 assert.equal(autosaveRecoveryDecision(remote(4),draft,2,3),'conflict');
});
test('stable object-key order but not widget ordering is required for persisted proof',()=>{
 const reordered={...remote(3),page_design:{header:'Header',widgets:draft.widgets}};
 assert.equal(autosaveRecoveryDecision(reordered,draft,2),'persisted');
 const other={...draft,widgets:[draft.widgets[0],{id:'second'}]};
 assert.equal(autosaveRecoveryDecision(reordered,other,2),'conflict');
});
test('only transport failures can trigger a bounded automatic retry',()=>{
 for(const msg of ['Failed to fetch','NetworkError when attempting to fetch resource','Load failed','AbortError','HTTP 502','HTTP 503','HTTP 504','Timeout'])assert.equal(recoverableAutosaveTransportError(Error(msg)),true,msg);
 for(const msg of ['invalid_widget','design_revision_conflict','HTTP 400','HTTP 401','HTTP 409','HTTP 422'])assert.equal(recoverableAutosaveTransportError(Error(msg)),false,msg);
 assert.deepEqual([0,1,2,3,8].map(retryAutosaveDelay),[850,1700,3400,6500,6500]);
});
