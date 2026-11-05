import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {changeRehearsalReaction,commitRehearsalAnswer,REHEARSAL_REACTION_PREFIX} from '../src/rehearsal-responses.ts';
import {sampleStatisticRows} from '../src/widget-results.ts';
import {validPageDesign} from '../../api/src/domain.ts';

const source=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const server=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');

test('presenter rehearsal uses neutral projection components, never shared draft controls',()=>{
 for(const kind of ['reactions','rating'])assert.match(source,new RegExp(`kind===['"]${kind}['"].*viewer===['"]presenter['"]`));
 // RC128: the question and its submit control have the same structure in both
 // previews, but the presenter cannot alter or submit simulated answers.
 assert.match(source,/\(kind==='question'\|\|kind==='timed-quiz'\)\?<div className="projection-question-group"/);
 assert.match(source,/const canInteract=viewer==='participant'\&\&!pageExpired/);
 assert.match(source,/disabled=\{!canInteract\|\|!canSubmitRehearsalAnswer\(answerMode,current\)\}/);
 assert.match(source,/viewer==='presenter'\?'Invia risposta':'Invia risposta di prova'/);
 assert.match(source,/kind==='timed-quiz'\&\&<PageTimer/);
 // Authored presenter results widgets display aggregate simulations, never participant drafts.
 assert.match(source,/kind==='results-button'\?\(\(\)=>\{/);
 assert.match(source,/linkedStatisticContext\(w,viewActivity,activities,viewWidgets\)/);
 assert.match(source,/demoResultsVisible&&<section id=\"rehearsal-simulated-results\"/);
 assert.match(source,/const current=viewer==='participant'\?responses\[key\]:undefined/);
 assert.match(source,/sampleStatisticRows\(source,seed,submittedAnswers/);
 assert.match(source,/rehearsalFreeTextRows\(source,submittedAnswers/);
 assert.doesNotMatch(server,/\/api\/join\/.*\/reactions\/stats/);
});
test('choice control is ordered before its caption in the participant and rehearsal',()=>{
 assert.match(source,/<label className="widget-answer-option" style=\{answerOptionStyle\((?:marks|w)\.style\)\} key=\{o\.id\}><input type=/);
 assert.match(css,/\.widget-question \.widget-answer-option>input/);
 assert.match(css,/order:-1!important/);
 assert.match(css,/gap:\.35em!important/);
});
test('one rehearsal participant can replace a reaction, not increase the total number of votes',()=>{
 const pageKey=REHEARSAL_REACTION_PREFIX+'page-one';
 const widget={id:'reaction_1',kind:'reactions'};
 const start=sampleStatisticRows(widget,119,{});
 const first=changeRehearsalReaction({},pageKey,widget.id,'👍');
 const afterFirst=sampleStatisticRows(widget,119,first);
 assert.equal(afterFirst.find(x=>x.id==='👍')!.count,start.find(x=>x.id==='👍')!.count+1);
 const second=changeRehearsalReaction(first,pageKey,widget.id,'❤️');
 const afterSecond=sampleStatisticRows(widget,119,second);
 assert.equal(afterSecond.find(x=>x.id==='👍')!.count,start.find(x=>x.id==='👍')!.count);
 assert.equal(afterSecond.find(x=>x.id==='❤️')!.count,start.find(x=>x.id==='❤️')!.count+1);
 assert.equal(changeRehearsalReaction(second,pageKey,widget.id,'❤️'),second);
 assert.equal(Object.keys(second).length,2);
});
test('preview results include only sent answers and count each multiple choice independently',()=>{
 const widget={id:'poll1',kind:'question',options:[{id:'a',label:'Alpha'},{id:'b',label:'Beta'}]};
 const baseline=sampleStatisticRows(widget,999,{});
 const draft=['a','b'];
 assert.deepEqual(sampleStatisticRows(widget,999,{}),baseline);
 const after=sampleStatisticRows(widget,999,commitRehearsalAnswer({},'poll1',draft,'multiple'));
 for(const id of ['a','b'])assert.equal(after.find(x=>x.id===id)!.count,baseline.find(x=>x.id===id)!.count+1);
});
test('response replacement remains opt-in and author-controlled',()=>{
 const normal={widgets:[{id:'q',kind:'question',answerMode:'single',options:[{id:'a',label:'A'},{id:'b',label:'B'}]}]};
 assert.equal(validPageDesign(normal),true);
 assert.equal(validPageDesign({widgets:[{...normal.widgets[0],allowAnswerChange:true}]}),true);
 assert.equal(validPageDesign({widgets:[{...normal.widgets[0],allowAnswerChange:'yes'}]}),false);
 assert.match(server,/existing\.rowCount&&part\.allowAnswerChange!==true/);
 assert.match(server,/FOR UPDATE/);
 assert.match(server,/UPDATE widget_answers SET answer_mode=/);
 assert.match(server,/if\(!timing\.valid\)/);
 assert.match(source,/Consenti al partecipante di modificare la risposta inviata/);
});
test('live reactions replace choice in PostgreSQL and refresh authenticated aggregates',()=>{
 assert.match(server,/ON CONFLICT\(activity_id,participant_id\) DO UPDATE SET emoji=EXCLUDED\.emoji/);
 assert.match(server,/page_reactions\.emoji IS DISTINCT FROM EXCLUDED\.emoji/);
 assert.match(server,/if\(r\.rowCount\)await broadcast\(s\.id\)/);
 // RC160 reactions are authored widgets only: no unconditional reaction bar
 // after the slide. The shared widget still sends a selected emoji.
 assert.match(source,/w\.kind==='reactions'\?<div className="projection-sample-reactions"/);
 assert.match(source,/selected=\{selectedReaction\} onSelect=\{emoji=>void react\(emoji\)\}/);
 const participant=source.slice(source.indexOf('{joinPath?<main'),source.indexOf('publicPath?<PresenterLiveScreen'));
 assert.doesNotMatch(participant,/className="reaction-bar"/);
});

test('profile previews show authenticated name/photo and public email only when opted in',()=>{
 assert.match(source,/function EditorPresenterProfileWidget/);
 assert.match(source,/usePrivateProfile=\{true\}/);
 assert.match(source,/showEmail=\{widget.showEmail===true\}/);
 assert.match(source,/p\.profile_photo_url/);
 assert.match(source,/p\.name/);
});
