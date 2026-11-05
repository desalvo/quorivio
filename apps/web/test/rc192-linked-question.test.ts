import test from 'node:test';
import assert from 'node:assert/strict';
import {linkedResultQuestion,linkedStatisticContext} from '../src/widget-results.ts';
const source={id:'original',kind:'question',label:'Domanda originale',description:'Sottotitolo',options:[{id:'a',label:'Risposta A'},{id:'b',label:'Risposta B'}],questions:[{id:'sub',label:'Seconda domanda',options:[{id:'c',label:'Risposta C'}]}]};
const result={id:'results',kind:'results-button',targetActivityId:'page-a',targetWidgetId:'original',showSourceQuestion:true};
test('optional source question is hidden unless explicitly enabled',()=>{
 assert.equal(linkedResultQuestion({...result,showSourceQuestion:false},source),undefined);
 assert.equal(linkedResultQuestion({...result,showSourceQuestion:undefined},source),undefined);
 assert.deepEqual(linkedResultQuestion(result,source),{part:{id:undefined,label:'Domanda originale',description:'Sottotitolo',answerMode:undefined,options:source.options},questionId:''});
});
test('independent subquestion carries its own title/options and field id',()=>{
 const selected=linkedResultQuestion({...result,targetQuestionId:'sub'},source);
 assert.equal(selected?.part.label,'Seconda domanda');
 assert.deepEqual(selected?.part.options,[{id:'c',label:'Risposta C'}]);
 assert.equal(selected?.questionId,'sub');
 assert.equal(linkedResultQuestion({...result,targetQuestionId:'bad'},source),undefined);
});
test('cross-page source resolution supports the optional read-only header without exposing result widgets to participants',()=>{
 const pages=[{id:'page-a',page_design:{widgets:[source]}},{id:'page-b',page_design:{widgets:[result]}}];
 const context=linkedStatisticContext(result,pages[1],pages,pages[1].page_design.widgets);
 assert.equal(context?.activity.id,'page-a');
 assert.equal(linkedResultQuestion(result,context!.source)?.part.label,'Domanda originale');
});
