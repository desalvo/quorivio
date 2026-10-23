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
