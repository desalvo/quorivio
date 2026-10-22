import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign,validateSubmittedAnswer} from '../src/domain.ts';
test('independent single-choice question has its own options',()=>{
 const options=[{id:'yes',label:'Sì'},{id:'no',label:'No'}];
 assert.equal(validPageDesign({widgets:[{id:'q1',kind:'question',answerMode:'single',options,required:true}]}),true);
 assert.deepEqual(validateSubmittedAnswer('single',true,'yes',options)?.optionIds,['yes']);
 assert.equal(validateSubmittedAnswer('single',true,'unknown',options),null);
});
test('multiple question validates distinct options',()=>{
 const options=[{id:'a',label:'A'},{id:'b',label:'B'}];
 assert.equal(validPageDesign({widgets:[{id:'a1',kind:'question',answerMode:'multiple',options},{id:'a2',kind:'question',answerMode:'text'}]}),true);
 assert.equal(validateSubmittedAnswer('multiple',true,['a','a'],options),null);
 assert.deepEqual(validateSubmittedAnswer('multiple',true,['a','b'],options)?.optionIds,['a','b']);
});
test('widget options reject duplicates and oversize labels',()=>{
 assert.equal(validPageDesign({widgets:[{id:'q',kind:'question',options:[{id:'a',label:'A'},{id:'a',label:'B'}]}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'q',kind:'question',options:[{id:'a',label:'x'.repeat(161)}]}]}),false);
});
