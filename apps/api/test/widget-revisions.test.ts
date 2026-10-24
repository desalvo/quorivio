import test from 'node:test';
import assert from 'node:assert/strict';
import {widgetAnswerShapeChanged,aggregateWidgetAnswerRevisions,liveTimedWidgetMutation} from '../src/widget-revisions.ts';

test('label and formatting do not change answer semantics',()=>{
 const a={id:'w1',kind:'question',answerMode:'single',required:true,options:[{id:'a',label:'A'}]};
 assert.equal(widgetAnswerShapeChanged(a,{...a,label:'New heading',style:{bold:true}}),false);
});
test('changing options, mode or obligation changes revision',()=>{
 const a={answerMode:'single',required:true,options:[{id:'a',label:'A'}]};
 assert.equal(widgetAnswerShapeChanged(a,{...a,answerMode:'multiple'}),true);
 assert.equal(widgetAnswerShapeChanged(a,{...a,required:false}),true);
 assert.equal(widgetAnswerShapeChanged(a,{...a,options:[{id:'b',label:'B'}]}),true);
});
test('analytics separate old and new revisions',()=>{
 const r=aggregateWidgetAnswerRevisions([{revision:1,answer_mode:'single',answer_payload:{optionIds:['a']}},{revision:2,answer_mode:'multiple',answer_payload:{optionIds:['b','c']}},{revision:2,answer_mode:'multiple',answer_payload:{optionIds:['b']}}]);
 assert.deepEqual(r,[{revision:1,responses:1,options:{a:1},texts:0,attachments:0},{revision:2,responses:2,options:{b:2,c:1},texts:0,attachments:0}]);
});

test('timed quiz answer keys and durations trigger revisions',()=>{
 const w={id:'t1',kind:'timed-quiz',answerMode:'single',options:[{id:'a',label:'A'},{id:'b',label:'B'}],correctOptionId:'a',durationSeconds:30};
 assert.equal(widgetAnswerShapeChanged(w,{...w,correctOptionId:'b'}),true);
 assert.equal(widgetAnswerShapeChanged(w,{...w,durationSeconds:45}),true);
 assert.equal(widgetAnswerShapeChanged(w,{...w,position:{x:10,y:20}}),false);
 assert.equal(liveTimedWidgetMutation([w],[{...w,correctOptionId:'b'}]),true);
 assert.equal(liveTimedWidgetMutation([w],[]),true);
 assert.equal(liveTimedWidgetMutation([w],[{...w,position:{x:1}}]),false);
});

test('single-choice timed quiz legacy and modern answer-key encodings share a revision',()=>{
 const old={id:'t',kind:'timed-quiz',options:[{id:'a',label:'A'}],correctOptionId:'a'};
 assert.equal(widgetAnswerShapeChanged(old,{...old,correctOptionIds:[]}),false);
 assert.equal(widgetAnswerShapeChanged(old,{...old,correctOptionId:undefined,correctOptionIds:['a'],answerMode:'single',durationSeconds:30}),false);
 assert.equal(liveTimedWidgetMutation([old],[{...old,correctOptionIds:[]}]),false);
 assert.equal(widgetAnswerShapeChanged(old,{...old,correctOptionId:undefined,correctOptionIds:['b']}),true);
});
test('multiple-choice quiz retains distinct answer-key semantics',()=>{
 const old={id:'t',kind:'timed-quiz',answerMode:'multiple',correctOptionIds:['a','b']};
 assert.equal(widgetAnswerShapeChanged(old,{...old,correctOptionId:'a'}),false);
 assert.equal(widgetAnswerShapeChanged(old,{...old,correctOptionIds:['a']}),true);
});


test('widget results safely count reserved option identifiers and deduplicate historical answers',()=>{
 const rows=[{revision:1,answer_mode:'multiple',answer_payload:{optionIds:['__proto__','__proto__','constructor','a']}},{revision:1,answer_mode:'single',answer_payload:{optionIds:['__proto__']}}];
 const actual=aggregateWidgetAnswerRevisions(rows);
 assert.equal(actual[0].responses,2);
 assert.deepEqual(Object.entries(actual[0].options).sort(),[['__proto__',2],['a',1],['constructor',1]].sort());
 assert.equal(Object.getPrototypeOf(actual[0].options),Object.prototype);
});


test('historical malformed revision and payload do not corrupt grouped statistics',()=>{
 const rows:any[]=[
  {revision:NaN,answer_payload:{optionIds:['a']}},
  {revision:0,answer_payload:{optionIds:['a']}},
  {revision:1.5,answer_payload:{optionIds:['a']}},
  {revision:1,answer_payload:null},
  {revision:1,answer_payload:{optionIds:['constructor','toString','toString'],text:42,assetId:4}},
  {revision:1,answer_payload:{optionIds:['safe','bad id',7],text:'hello',assetId:'asset'}}
 ];
 const result=aggregateWidgetAnswerRevisions(rows);
 assert.deepEqual(result,[{revision:1,responses:3,options:{constructor:1,toString:1,safe:1},texts:1,attachments:1}]);
 assert.equal(Object.getPrototypeOf(result[0].options),Object.prototype);
 assert.equal(JSON.parse(JSON.stringify(result))[0].options.constructor,1);
});

test('live timed mutation rejects duplicate and missing widget IDs before lookup',()=>{
 const quiz={id:'quiz',kind:'timed-quiz',answerMode:'single',correctOptionId:'a',options:[{id:'a',label:'A'}]};
 assert.equal(liveTimedWidgetMutation([quiz],[quiz,{...quiz,correctOptionId:'b'}]),true);
 assert.equal(liveTimedWidgetMutation([quiz],[quiz,{kind:'text',id:'quiz'}]),true);
 assert.equal(liveTimedWidgetMutation([quiz],[quiz,{kind:'text'}]),true);
 assert.equal(liveTimedWidgetMutation([quiz],[quiz,{kind:'text',id:'other'}]),false);
});
