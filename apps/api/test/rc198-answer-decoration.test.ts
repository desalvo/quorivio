import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign,validWidgetTextStyle} from '../src/domain.ts';

const styledAnswer={fontFamily:'Georgia',underline:false,strikethrough:false,
 answerFontFamily:'Arial',answerUnderline:true,answerStrikethrough:true};

test('API persists independent underline and strikethrough for question answer text',()=>{
 assert.equal(validWidgetTextStyle(styledAnswer),true);
 for(const kind of ['question','timed-quiz','topic-question']){
  const design={widgets:[{id:'q',kind,label:'Domanda',answerMode:'single',
   options:[{id:'a',label:'Una risposta su più righe'}],style:styledAnswer}]};
  assert.equal(validPageDesign(design),true,kind);
 }
});

test('answer decoration schema is fail-closed and leaves old documents compatible',()=>{
 for(const key of ['answerUnderline','answerStrikethrough'] as const){
  for(const invalid of ['true',1,null,{},[]]){
   assert.equal(validWidgetTextStyle({...styledAnswer,[key]:invalid}),false,`${key}: ${String(invalid)}`);
  }
  assert.equal(validWidgetTextStyle({...styledAnswer,[key]:false}),true);
 }
 assert.equal(validWidgetTextStyle({answerFontFamily:'Arial',answerBold:false}),true);
 assert.equal(validWidgetTextStyle({answerTextDecoration:'underline'}),false);
});
