import test from 'node:test';
import assert from 'node:assert/strict';
import {questionRevisionAtHistory,widgetAnswerShapeChanged} from '../src/widget-revisions.ts';

const widget=(primary='a',first='a',second='a')=>({
 id:'survey',kind:'question',answerMode:'single',options:[{id:primary,label:primary}],
 questions:[{id:'q1',answerMode:'single',options:[{id:first,label:first}]},
 {id:'q2',answerMode:'single',options:[{id:second,label:second}]}],
});
const stages=[{revision:1,definition:widget()},
 {revision:2,definition:widget('a','b','a')},
 {revision:3,definition:widget('b','b','a')},
 {revision:4,definition:widget('b','b','c')}];

test('one changed subquestion never reopens or rescales independent answers',()=>{
 assert.equal(questionRevisionAtHistory(stages.slice(0,2),''),1);
 assert.equal(questionRevisionAtHistory(stages.slice(0,2),'q1'),2);
 assert.equal(questionRevisionAtHistory(stages.slice(0,2),'q2'),1);
 assert.equal(questionRevisionAtHistory(stages.slice(0,3),''),3);
 assert.equal(questionRevisionAtHistory(stages.slice(0,3),'q1'),2);
 assert.equal(questionRevisionAtHistory(stages,'q2'),4);
 assert.equal(questionRevisionAtHistory(stages,'q1'),2);
});
test('legacy row revision one remains stable when questions are added',()=>{
 const initial={id:'survey',kind:'question',answerMode:'single',options:[{id:'a',label:'A'}]};
 const plus={...initial,questions:[{id:'q1',answerMode:'text'}]};
 assert.equal(widgetAnswerShapeChanged(initial,plus),true);
 assert.equal(questionRevisionAtHistory([{revision:1,definition:initial},{revision:2,definition:plus}],''),1);
 assert.equal(questionRevisionAtHistory([{revision:1,definition:initial},{revision:2,definition:plus}],'q1'),2);
 assert.equal(questionRevisionAtHistory([],''),1);
});
test('removed then recreated question never inherits stale idempotency record',()=>{
 const removed={...widget(),questions:[widget().questions[1]]};
 const readded={...widget(),questions:[widget().questions[0],widget().questions[1]]};
 assert.equal(questionRevisionAtHistory([{revision:1,definition:widget()}, {revision:2,definition:removed}, {revision:3,definition:readded}],'q1'),3);
});
test('pure style and geometry changes do not reset independent answers',()=>{
 const old=widget();const styled={...old,style:{color:'#ffffff'},position:{x:15,y:15}};
 assert.equal(widgetAnswerShapeChanged(old,styled),false);
 assert.equal(questionRevisionAtHistory([{revision:1,definition:old},{revision:2,definition:styled}],'q1'),1);
});
test('a shared quiz timer change creates new revision for each timed question',()=>{
 const old={...widget(),kind:'timed-quiz',durationSeconds:20};
 const later={...old,durationSeconds:30};
 const history=[{revision:1,definition:old},{revision:2,definition:later}];
 for(const question of ['', 'q1', 'q2'])assert.equal(questionRevisionAtHistory(history,question),2);
});
test('timed answer keys remain question-scoped',()=>{
 const old={...widget(),kind:'timed-quiz',correctOptionId:'a',questions:[{id:'q1',answerMode:'single',correctOptionId:'a',options:[{id:'a',label:'A'}]},{id:'q2',answerMode:'single',correctOptionId:'b',options:[{id:'b',label:'B'}]}]};
 const next={...old,questions:[{...old.questions[0],correctOptionId:'b'},old.questions[1]]};
 const history=[{revision:1,definition:old},{revision:2,definition:next}];
 assert.equal(questionRevisionAtHistory(history,'q1'),2);
 assert.equal(questionRevisionAtHistory(history,'q2'),1);
 assert.equal(questionRevisionAtHistory(history,''),1);
});
