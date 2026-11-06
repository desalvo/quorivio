import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign} from '../src/domain.ts';
const base={id:'res',kind:'results-button'};
test('truth highlighting defaults off and is restricted to result widgets',()=>{
 assert.equal(validPageDesign({widgets:[{...base,showCorrectAnswers:false}]}),true);
 assert.equal(validPageDesign({widgets:[{...base,showCorrectAnswers:true}]}),true);
 for(const value of ['true',1,null])assert.equal(validPageDesign({widgets:[{...base,showCorrectAnswers:value}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'ordinary',kind:'text',showCorrectAnswers:true}]}),false);
});
test('per element font, colour and markup persist independently and fail closed',()=>{
 const text={sourceTitle:{fontFamily:'Georgia',fontSize:24,bold:true,color:'#123ABC'},'question:main':{color:'#246810',italic:true},'option:a':{color:'#abcdef',bold:false},'option:q1:a':{underline:true},'row:q1:a':{strikethrough:true}};
 assert.equal(validPageDesign({widgets:[{...base,resultTextStyles:text}]}),true);
 for(const bad of [
   {'option:a':{color:'red'}},{'option:a':{fontSize:999}},{'option:a':{fontFamily:'url(evil)'}},
   {'option:a':{script:'alert(1)'}},{'__proto__.hack':{color:'#000000'}},
   {'question:main':{bold:'true'}},Array(2),null]){
  assert.equal(validPageDesign({widgets:[{...base,resultTextStyles:bad}]}),false);
 }
 assert.equal(validPageDesign({widgets:[{id:'ordinary',kind:'text',resultTextStyles:text}]}),false);
});
