import test from 'node:test';import assert from 'node:assert/strict';
import {linkedResultQuestion,resultSourceTitleVisible,resultSourceAnswersVisible} from '../src/widget-results.ts';
const source={id:'original',kind:'question',label:'Titolo linked',options:[{id:'a',label:'Prima risposta'}]};
test('legacy result checkbox maps to both sections',()=>{
 const old={showSourceQuestion:true};assert.equal(resultSourceTitleVisible(old),true);assert.equal(resultSourceAnswersVisible(old),true);
 assert.equal(linkedResultQuestion(old,source)?.part.label,'Titolo linked');
 assert.equal(linkedResultQuestion({showSourceQuestion:false},source),undefined);
});
test('independent title and answers work in all combinations',()=>{
 for(const title of [false,true])for(const answers of [false,true]){
  const result={showSourceQuestion:true,showSourceTitle:title,showSourceAnswers:answers};
  assert.equal(resultSourceTitleVisible(result),title);
  assert.equal(resultSourceAnswersVisible(result),answers);
  assert.equal(!!linkedResultQuestion(result,source),title||answers);
 }
});
test('explicit false overrides legacy true and source question remains read-only',()=>{
 assert.equal(linkedResultQuestion({showSourceQuestion:true,showSourceTitle:false,showSourceAnswers:false},source),undefined);
 const selected=linkedResultQuestion({showSourceTitle:true,showSourceAnswers:false},source);
 assert.equal(selected?.part.label,'Titolo linked');
 assert.equal('correct_option_id' in (selected?.part||{}),false);
});
