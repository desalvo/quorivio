import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validPageDesign,validWidgetSubquestions} from '../src/domain.ts';
import {widgetAnswerShapeChanged} from '../src/widget-revisions.ts';
const sub=(id:string)=>({id,label:'Una domanda',answerMode:'single',options:[{id:'a',label:'Sì'},{id:'b',label:'No'}]});
const page=(widget:any)=>({widgets:[widget]});
const base={id:'widget1',kind:'question',label:'Principale',answerMode:'text'};
const sql=readFileSync(new URL('../src/schema.sql',import.meta.url),'utf8');
const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
test('accepts up to five independent questions with separate IDs in same widget',()=>{
 assert.equal(validPageDesign(page({...base,questions:[sub('q1'),sub('q2')]})),true);
 assert.equal(validWidgetSubquestions(Array.from({length:5},(_,i)=>sub('q'+i)),'question'),true);
 assert.equal(validWidgetSubquestions(Array.from({length:6},(_,i)=>sub('q'+i)),'question'),false);
 assert.equal(validPageDesign(page({...base,questions:[sub('q1'),sub('q1')]})),false);
 assert.equal(validPageDesign(page({...base,questions:[sub('../escape')]})),false);
 assert.equal(validPageDesign(page({...base,questions:[{id:'q1',label:'Test',answerMode:'single',options:[{id:'only',label:'Only'}]}]})),false);
 assert.equal(validPageDesign(page({...base,questions:[sub('q1')],textMarks:[{field:'question:q1:label',start:0,end:3,style:{bold:true}}]})),true);
 assert.equal(validPageDesign(page({...base,questions:[sub('q1')],textMarks:[{field:'question:q2:label',start:0,end:3,style:{bold:true}}]})),false);
});
test('legacy widget without questions stays accepted and adding independent questions changes revision',()=>{
 assert.equal(validPageDesign(page(base)),true);
 assert.equal(widgetAnswerShapeChanged(base,{...base,questions:[sub('q1')]}),true);
 assert.equal(widgetAnswerShapeChanged({...base,questions:[sub('q1')]},{...base,questions:[sub('q1')],style:{color:'#ffffff'}}),false);
});
test('PostgreSQL migration isolates per participant, widget, question and revision; legacy question_id empty',()=>{
 assert.match(sql,/ADD COLUMN IF NOT EXISTS question_id text NOT NULL DEFAULT ''/);
 assert.match(sql,/DROP INDEX IF EXISTS widget_answers_one_per_revision/);
 assert.match(sql,/CREATE UNIQUE INDEX IF NOT EXISTS widget_answers_one_per_question_revision ON widget_answers\(activity_id,participant_id,widget_id,question_id,revision\)/);
 assert.match(server,/const part=questionId\?questions\.find/);
 assert.match(server,/ON CONFLICT\(activity_id,participant_id,widget_id,question_id,revision\) DO NOTHING/);
 assert.match(server,/AND question_id=\$4 AND revision=\$5/);
 assert.match(server,/question_id=\$4 ORDER BY submitted_at/);
});
test('presenter results can target a defined independent question, never arbitrary question IDs',()=>{
 const source={...base,questions:[sub('q1')]};
 const chart={id:'chart',kind:'results-button',targetWidgetId:'widget1',targetQuestionId:'q1'};
 assert.equal(validPageDesign({widgets:[source,chart]}),true);
 assert.equal(validPageDesign({widgets:[source,{...chart,targetQuestionId:'q2'}]}),false);
 assert.equal(validPageDesign({widgets:[source,{...chart,targetQuestionId:'../../foo'}]}),false);
});

test('presenter summary and timed ranking cannot mix independent question responses',()=>{
 assert.match(server,/SELECT activity_id,widget_id,question_id,revision,answer_mode,count\(\*\)::int AS responses/);
 const start=server.indexOf("app.get('/api/sessions/:id/activities/:aid/widgets/:wid/timed-leaderboard'");
 const stop=server.indexOf("app.get('/api/sessions/:id/activities/:aid/timed-leaderboard'",start);
 const rank=server.slice(start,stop);
 assert.match(rank,/AND question_id=\$4/);
 assert.match(rank,/AND w.question_id=\$4/);
 assert.match(rank,/question_id:questionId/);
});
test('public activity projection redacts nested timed quiz answer keys but leaves presentation labels',async()=>{
 const {publicActivity}=await import('../src/domain.ts');
 const activity:any={id:'a',type:'timed_quiz',correct_option_id:'hidden',correct_option_ids:['a'],page_design:{widgets:[{id:'quiz',kind:'timed-quiz',label:'Question one',correctOptionId:'private',options:[{id:'a',label:'A'}],questions:[{id:'sub1',label:'Second question',correctOptionId:'secret',correctOptionIds:['b'],options:[{id:'b',label:'B'}]}]}]}};
 const audience=publicActivity(activity) as any;
 assert.equal(audience.correct_option_id,undefined);
 assert.equal(audience.correct_option_ids,undefined);
 assert.equal(audience.page_design.widgets[0].correctOptionId,undefined);
 assert.equal(audience.page_design.widgets[0].questions[0].correctOptionId,undefined);
 assert.equal(audience.page_design.widgets[0].questions[0].correctOptionIds,undefined);
 assert.equal(audience.page_design.widgets[0].questions[0].label,'Second question');
 assert.equal(activity.page_design.widgets[0].questions[0].correctOptionId,'secret');
});
