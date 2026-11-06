import test from 'node:test';
import assert from 'node:assert/strict';
import {validResultTextStyles,resultTextCss,resultElementKey,resultHasAnswerKey,resultTrueOptionIds} from '../src/result-text-style.ts';
const source={id:'src',kind:'question',label:'Quiz',answerMode:'multiple',answerKeyEnabled:true,
 options:[{id:'a',label:'A'},{id:'b',label:'B'},{id:'c',label:'C'}],correctOptionIds:['a','c']};
test('truth flags are never inferred without an explicit grading key',()=>{
 assert.equal(resultHasAnswerKey(source),true);
 assert.deepEqual(resultTrueOptionIds(source),['a','c']);
 assert.deepEqual(resultTrueOptionIds({...source,answerKeyEnabled:false}),[]);
 assert.equal(resultHasAnswerKey({...source,answerKeyEnabled:false}),false);
 assert.deepEqual(resultTrueOptionIds({...source,correctOptionIds:['x','a','a']}),['a']);
});
test('each subquestion and option has an independent and bounded style',()=>{
 const a=resultElementKey('option','first','a'),b=resultElementKey('option','second','a');
 assert.notEqual(a,b);
 const fmt={[a]:{fontFamily:'Arial',fontSize:18,color:'#ff0000',bold:false,italic:true,underline:true},[b]:{color:'#00ff00'}};
 assert.equal(validResultTextStyles(fmt),true);
 assert.equal(resultTextCss(fmt,a,{bold:true}).fontWeight,400);
 assert.equal(resultTextCss(fmt,a).fontStyle,'italic');
 assert.equal(resultTextCss(fmt,b).color,'#00ff00');
 assert.equal(validResultTextStyles({'option:a':{color:'javascript:evil'}}),false);
});
test('only a source question with a key can reveal true answers',()=>{
 const nested={...source,questions:[{id:'one',answerMode:'single',answerKeyEnabled:true,options:source.options,correctOptionId:'b'},
 {id:'two',answerMode:'single',answerKeyEnabled:false,options:source.options,correctOptionId:'c'}]};
 assert.deepEqual(resultTrueOptionIds(nested,'one'),['b']);
 assert.deepEqual(resultTrueOptionIds(nested,'two'),[]);
 assert.deepEqual(resultTrueOptionIds(nested,'missing'),[]);
});
