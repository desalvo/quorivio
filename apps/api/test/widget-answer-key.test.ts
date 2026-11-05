import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validPageDesign,publicActivity,publicTheme} from '../src/domain.ts';
import {answerKeyIds,setChoiceTruth,clearChoiceTruth,gradeChoiceAnswer,hasAnswerKey} from '../src/widget-answer-key.ts';
import {widgetAnswerShapeChanged,questionRevisionAtHistory} from '../src/widget-revisions.ts';
const opts=[{id:'a',label:'Acqua'},{id:'b',label:'Terra'},{id:'c',label:'Fuoco'}];
const base={id:'q1',kind:'question',label:'Quale?',answerMode:'single',options:opts};
const page=(w:any)=>({widgets:[w]});

test('optional key keeps legacy question free from correction or answer disclosure',()=>{
 assert.equal(validPageDesign(page(base)),true);
 assert.equal(hasAnswerKey(base,'question'),false);
 assert.equal(gradeChoiceAnswer(base,'question',['a']),null);
 const ungraded=publicActivity({id:'page',type:'slide',page_design:page(base)} as any) as any;
 assert.equal(ungraded.page_design.widgets[0].correctOptionIds,undefined);
});

test('first explicit truth value enables all-false defaults, reset disables feedback',()=>{
 const wrong=setChoiceTruth(base,'b',false);
 assert.deepEqual(wrong,{answerKeyEnabled:true,correctOptionId:undefined,correctOptionIds:[]});
 assert.equal(gradeChoiceAnswer({...base,...wrong},'question',['a'])?.is_correct,false);
 const keyed={...base,...setChoiceTruth(base,'a',true)};
 assert.deepEqual(answerKeyIds(keyed),['a']);
 assert.equal(gradeChoiceAnswer(keyed,'question',['a'])?.is_correct,true);
 assert.equal(gradeChoiceAnswer(keyed,'question',['b'])?.is_correct,false);
 assert.deepEqual(gradeChoiceAnswer(keyed,'question',['b'])?.choices.map(c=>c.correct),[true,false,false]);
 assert.equal(gradeChoiceAnswer({...keyed,...clearChoiceTruth()},'question',['b']),null);
 assert.equal(validPageDesign(page(keyed)),true);
 assert.equal(validPageDesign(page({...keyed,...clearChoiceTruth()})),true);
});

test('single-choice truth is exclusive and multi-choice requires exact set equality',()=>{
 const first={...base,...setChoiceTruth(base,'a',true)};
 const second={...first,...setChoiceTruth(first,'b',true)};
 assert.deepEqual(answerKeyIds(second),['b']);
 assert.equal(gradeChoiceAnswer(second,'question',['a'])?.is_correct,false);
 assert.equal(gradeChoiceAnswer(second,'question',['b'])?.is_correct,true);
 const multi={...base,answerMode:'multiple' as const};
 const m1={...multi,...setChoiceTruth(multi,'a',true)};
 const m2={...m1,...setChoiceTruth(m1,'c',true)};
 assert.deepEqual(answerKeyIds(m2),['a','c']);
 assert.equal(gradeChoiceAnswer(m2,'question',['a','c'])?.is_correct,true);
 assert.equal(gradeChoiceAnswer(m2,'question',['c','a'])?.is_correct,true);
 assert.equal(gradeChoiceAnswer(m2,'question',['a'])?.is_correct,false);
 assert.equal(gradeChoiceAnswer(m2,'question',['a','b','c'])?.is_correct,false);
 assert.equal(gradeChoiceAnswer(m2,'question',['a','a'])?.is_correct,false);
 assert.equal(validPageDesign(page(m2)),true);
 assert.equal(validPageDesign(page({...base,answerKeyEnabled:true,correctOptionIds:['a','c']})),false);
 assert.throws(()=>setChoiceTruth(base,'outside',true),/Unknown choice/);
});

test('nested independent question has its own key and public projection redacts both',()=>{
 const sub={id:'sub',label:'Sub',answerMode:'multiple',options:opts,answerKeyEnabled:true,correctOptionIds:['a','b']};
 const primary={...base,answerKeyEnabled:true,correctOptionId:'c',correctOptionIds:['c'],questions:[sub]};
 assert.equal(validPageDesign(page(primary)),true);
 const audience=publicActivity({id:'page',type:'slide',page_design:page(primary)} as any) as any;
 const pub=audience.page_design.widgets[0];
 assert.equal(pub.answerKeyEnabled,true);
 assert.equal(pub.correctOptionId,undefined);
 assert.equal(pub.correctOptionIds,undefined);
 assert.equal(pub.questions[0].correctOptionIds,undefined);
 assert.equal(pub.questions[0].answerKeyEnabled,true);
 const extra=publicActivity({id:'page',type:'slide',result_design:page(primary)} as any) as any;
 assert.equal(extra.result_design.widgets[0].correctOptionId,undefined);
 assert.equal(extra.result_design.widgets[0].questions[0].correctOptionIds,undefined);
 const theme=publicTheme({master:{widgets:[primary]}}) as any;
 assert.equal(theme.master.widgets[0].correctOptionId,undefined);
 assert.equal(theme.master.widgets[0].questions[0].correctOptionIds,undefined);
 assert.equal(gradeChoiceAnswer(sub,'question',['a','b'])?.is_correct,true);
 assert.equal(validPageDesign(page({...base,questions:[{...sub,answerKeyEnabled:'yes'}]})),false);
});

test('changing answer keys changes grading revision but visual styles do not',()=>{
 const original={...base,answerKeyEnabled:true,correctOptionId:'a'};
 const changed={...original,correctOptionId:'b'};
 assert.equal(widgetAnswerShapeChanged(original,changed),true);
 assert.equal(widgetAnswerShapeChanged(original,{...original,style:{fontSize:20}}),false);
 assert.equal(widgetAnswerShapeChanged(base,original),true);
 assert.equal(widgetAnswerShapeChanged(original,{...original,...clearChoiceTruth()}),true);
 const history=[{revision:1,definition:original},{revision:2,definition:changed}];
 assert.equal(questionRevisionAtHistory(history,''),2);
 const nestedBase={...base,questions:[{id:'q2',label:'Nested',answerMode:'single',options:opts,answerKeyEnabled:true,correctOptionId:'a'}]};
 const nestedNext={...nestedBase,questions:[{...nestedBase.questions[0],correctOptionId:'b'}]};
 assert.equal(questionRevisionAtHistory([{revision:1,definition:nestedBase},{revision:2,definition:nestedNext}],'q2'),2);
});

test('response endpoint returns feedback only after persisted submission; idempotent retries use stored answer',()=>{
 const s=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
 const route=s.slice(s.indexOf("app.post('/api/join/:code/activities/:aid/widgets/:wid/respond'"),s.indexOf("app.get('/api/sessions/:id/widget-answers'"));
 assert.match(route,/const feedback=gradeChoiceAnswer\(part,widget.kind,answer.optionIds\)/);
 assert.match(route,/if\(existing.rowCount&&part.allowAnswerChange!==true\)/);
 assert.match(route,/gradeChoiceAnswer\(part,widget.kind,existing.rows\[0\].answer_payload\?\.optionIds\)/);
 assert.match(route,/await cx.query\('COMMIT'\)/);
 assert.match(route,/const stored=r.rowCount\?answer.optionIds:/);
 assert.match(route,/\.\.\.\(submittedFeedback\?\{feedback:submittedFeedback\}:\{\}\)/);
 assert.doesNotMatch(s.slice(s.indexOf('function participantSnapshot('),s.indexOf('const webRoot=')),/gradeChoiceAnswer|answerKeyIds|correctOptionIds/);
});
