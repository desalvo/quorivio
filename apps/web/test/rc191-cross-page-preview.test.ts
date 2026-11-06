import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {rehearsalPresenterPages,rehearsalAudiencePage,rehearsalStartIndex} from '../src/rehearsal-page-routing.ts';
import {linkedStatisticContext,effectiveResultView,sampleStatisticRows,rowsFromWidgetAnswerDetail} from '../src/widget-results.ts';

const question={id:'question',title:'Domanda segreta al presentatore',page_design:{presenterHidden:true,widgets:[{id:'q',kind:'question',label:'Quale scegli?',answerMode:'single',options:[{id:'a',label:'Scelta A'},{id:'b',label:'Scelta B'}],resultsView:'pie'}]}};
const resultWidget={id:'result',kind:'results-button',label:'Risultati live',targetWidgetId:'q',targetActivityId:'question'};
const results={id:'results',title:'Risultati',page_design:{audiencePageId:'question',widgets:[resultWidget]}};
const outro={id:'outro',title:'Conclusioni',page_design:{widgets:[]}};
const pages=[question,results,outro];

test('both panes use independent source pages: presenter results and hidden audience question',()=>{
 const visible=rehearsalPresenterPages(pages);
 assert.deepEqual(visible.map(p=>p.id),['results','outro']);
 assert.equal(rehearsalAudiencePage(visible[0],pages)?.id,'question');
 assert.equal(rehearsalAudiencePage(visible[1],pages)?.id,'outro');
 assert.equal(rehearsalStartIndex(pages,'question'),0);
 assert.equal(rehearsalStartIndex(pages,'results'),0);
 assert.equal(rehearsalStartIndex(pages,'outro'),1);
 assert.equal(rehearsalStartIndex(pages,'unknown'),0);
});
test('cross-page results resolve source and chart from the hidden audience page',()=>{
 const context=linkedStatisticContext(resultWidget,results,pages);
 assert.equal(context?.activity.id,'question');
 assert.equal(context?.source.id,'q');
 assert.equal(effectiveResultView(resultWidget,context!.widgets),'pie');
 assert.deepEqual(rowsFromWidgetAnswerDetail(context!.source,{revisions:[{options:{a:4,b:1}}]}).map(r=>r.count),[4,1]);
 const sample=sampleStatisticRows(context!.source,42);
 assert.equal(sampleStatisticRows(context!.source,42,{q:'a'})[0].count,sample[0].count+1);
});
test('same-page links and missing/cross-session sources remain fail-closed',()=>{
 const own={id:'same',page_design:{widgets:[question.page_design.widgets[0],{...resultWidget,targetActivityId:undefined}]}};
 assert.equal(linkedStatisticContext(own.page_design.widgets[1],own,[own])?.source.id,'q');
 assert.equal(linkedStatisticContext({...resultWidget,targetActivityId:'missing'},results,pages),undefined);
 assert.equal(linkedStatisticContext({...resultWidget,targetWidgetId:'missing'},results,pages),undefined);
 const outOfSession={id:'foreign',page_design:{widgets:[question.page_design.widgets[0]]}};
 assert.equal(linkedStatisticContext({...resultWidget,targetActivityId:'foreign'},results,pages),undefined);
 assert.equal(rehearsalAudiencePage({...results,page_design:{...results.page_design,audiencePageId:'foreign'}},pages)?.id,'results');
 assert.ok(outOfSession);
});
test('rehearsal uses separate presenter/audience widgets and tracks only presenter-visible pages',()=>{
 const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 const section=main.split('function SessionRehearsal(',2)[1].split('const editorWidgetKinds',1)[0];
 for(const expected of [
  'const presenterPages=rehearsalPresenterPages(activities)',
  'const audienceActivity=rehearsalAudiencePage(activity,activities)',
  "const viewActivity=viewer==='presenter'?activity:audienceActivity",
  "const viewWidgets=viewer==='presenter'?presenterWidgets:widgets",
  'linkedStatisticContext(w,viewActivity,activities,viewWidgets)',
  'disabled={page>=presenterPages.length-1}',
  'participantPhoneLayout(widgets,audienceActivity?.page_design?.mobile).height',
 ])assert.ok(section.includes(expected),`Missing wiring: ${expected}`);
 assert.doesNotMatch(section,/const activity=activities\[page\]/);
 assert.doesNotMatch(section,/linkedStatisticSource\(w,widgets\)/);
});
test('live projection uses the same cross-page resolver with the source activity id',()=>{
 const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 const live=main.split('function PresenterLinkedResult(',2)[1].split('function ProjectedQuestionPart',1)[0];
 assert.match(live,/linkedStatisticContext\(widget,activity,activities,widgets\)/);
 assert.match(live,/const sourceActivityId=context\?\.activity\.id\|\|activity\.id/);
 assert.match(live,/widget-answers\/detail\?activity_id=\$\{encodeURIComponent\(sourceActivityId\)\}/);
 assert.match(live,/results temporarily|Risultati temporaneamente non disponibili/);
 assert.match(live,/window\.setInterval\(\(\)=>void load\(\),3000\)/);
 assert.doesNotMatch(live,/liveRevision/,'live snapshot updates must not cancel every in-flight source stats HTTP request');
 assert.match(live,/LinkedResultChart widget=\{\{\.\.\.widget,showCorrectAnswers:showCorrectLive\}\}/);
 assert.match(live,/resultHasAnswerKey\(source,widget\.targetQuestionId/);
 assert.match(live,/setShowCorrectLive\(e\.target\.checked\)/);

});
