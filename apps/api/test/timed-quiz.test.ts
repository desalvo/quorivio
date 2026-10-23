import test from 'node:test';
import assert from 'node:assert/strict';
import {checkAnswer,validPageDesign,publicActivity} from '../src/domain.ts';
test('timed quiz scores only matching answers',()=>{
 const quiz={type:'timed_quiz' as const,correct_option_id:'a',options:[{id:'a',label:'A'},{id:'b',label:'B'}]};
 assert.equal(checkAnswer(quiz,'a'),true);assert.equal(checkAnswer(quiz,'b'),false);
});
test('timed and presenter-only result widgets have independent layout',()=>{
 assert.equal(validPageDesign({widgets:[{id:'timed',kind:'timed-quiz',position:{x:0,y:0,width:55,height:55}},{id:'results',kind:'results-button',position:{x:60,y:65,width:30,height:20,rotation:0}}]}),true);
});
test('public quiz payload never discloses correct options',()=>{
 const quiz={id:'id',session_id:'s',type:'timed_quiz' as const,title:'Q',options:[],correct_option_id:'secret',correct_option_ids:['secret'],duration_seconds:30,status:'open' as const,position:0};
 const result=publicActivity(quiz);
 assert.equal('correct_option_id' in result,false);assert.equal('correct_option_ids' in result,false);
});
