import test from 'node:test';import assert from 'node:assert/strict';
import {validPageDesign} from '../src/domain.ts';
const item={id:'results',kind:'results-button'};
test('linked title and answers persist independently with valid theme colour',()=>{
 for(const title of [true,false])for(const answers of [true,false])assert.equal(validPageDesign({widgets:[{...item,showSourceTitle:title,showSourceAnswers:answers,style:{sourceQuestionColor:'#2563eb'}}]}),true);
 assert.equal(validPageDesign({widgets:[{...item,showSourceTitle:true,showSourceAnswers:'true'}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'text',kind:'text',showSourceTitle:true}]}),false);
 for(const hex of ['red','#12345','#GGFF00','url(javascript:...)'])assert.equal(validPageDesign({widgets:[{...item,style:{sourceQuestionColor:hex}}]}),false);
 assert.equal(validPageDesign({widgets:[{...item,showSourceQuestion:true}]}),true);
});
