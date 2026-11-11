import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {sortedResultBars,visibleResultBars,resultBarWidth} from '../src/result-top-rows.ts';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const api=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');
const domain=readFileSync(new URL('../../api/src/domain.ts',import.meta.url),'utf8');
const rating=readFileSync(new URL('../src/rating-choices.tsx',import.meta.url),'utf8');
const input=[{id:'0',count:8},{id:'1',count:15},{id:'2',count:0},{id:'3',count:15}];
test('RC305 four independent orderings are stable and never mutate source',()=>{
 const expected={'index-asc':['0','1','2','3'],'index-desc':['3','2','1','0'],'count-asc':['2','0','1','3'],'count-desc':['1','3','0','2']};
 for(const [order,ids] of Object.entries(expected))assert.deepEqual(sortedResultBars(input,order).map(x=>x.id),ids);
 assert.deepEqual(input.map(x=>x.id),['0','1','2','3']);
});
test('RC305 sorting occurs before limiting visible rows',()=>{
 assert.deepEqual(visibleResultBars(input,'count-asc',2).map(x=>x.id),['2','0']);
 assert.deepEqual(visibleResultBars(input,'index-desc',2).map(x=>x.id),['3','2']);
 assert.deepEqual(visibleResultBars(input,'count-desc',2).map(x=>x.id),['1','3']);
});
test('RC305 malformed order falls back to descending votes',()=>{
 assert.deepEqual(sortedResultBars(input,'invalid').map(x=>x.id),['1','3','0','2']);
});
test('RC305 maximum displayed bar is always 100% with safe zero handling',()=>{
 assert.equal(resultBarWidth(22,22),100);
 assert.equal(resultBarWidth(11,22),50);
 assert.equal(resultBarWidth(0,0),0);
 assert.equal(resultBarWidth(20,0),0);
 assert.equal(resultBarWidth(Number.NaN,22),0);
 assert.equal(resultBarWidth(100,22),100);
});
test('RC305 React rows use maximum of visible bars and source widget kind',()=>{
 assert.ok(ui.includes('visibleResultBars(data,widget.resultSortOrder,widget.resultTopCount)'));
 assert.ok(ui.includes('resultBarWidth(r.count,maxBarCount)'));
 assert.ok(ui.includes('data-result-source-kind={source.kind}'));
 assert.ok(ui.includes('aria-label="Ordinamento risposte risultati"'));
 for(const value of ['count-desc','count-asc','index-asc','index-desc'])assert.ok(ui.includes('<option value="'+value+'">'));
});
test('RC305 old content-fit max-content rows are overridden to stretch bars',()=>{
 assert.ok(css.includes('.linked-results.result-view-bars .linked-results-items .linked-results-row'));
 assert.ok(css.includes('align-self:stretch!important;box-sizing:border-box!important'));
 assert.ok(css.includes('.linked-results.result-view-bars{container-type:inline-size;}'));
 assert.ok(css.includes('font-size:clamp(14px,4.5cqw,54px)!important'));
});
test('RC305 privacy: read-only presenter never carries participant vote or comment',()=>{
 assert.ok(rating.includes("const current=!readOnly&&selected!==undefined"));
 assert.ok(rating.includes("value={readOnly?'':value}"));
 assert.ok(ui.includes("selected={viewer==='participant'&&typeof submittedAnswers[w.id]==='string'"));
 assert.ok(ui.includes("comment={viewer==='participant'?demoRatingComments[w.id]||'':''}"));
 assert.ok(ui.includes('if(kind===\'rating\')return <RatingStageContent widget={widget} readOnly/>'));
});
test('RC305 per-widget rating histogram is scoped to source, activity and session',()=>{
 assert.ok(api.includes('SELECT activity_id,widget_id,score,count(*)::int AS count FROM page_ratings WHERE session_id=$1'));
 assert.ok(api.includes('by_widget_score:byWidgetScore'));
 assert.ok(ui.includes("x.widget_id===source.id&&x.activity_id===sourceActivityId&&Number(x.score)===score"));
 assert.ok(ui.includes("Array.from({length:10},(_,score)=>"));
});
test('RC305 persisted sort modes validated fail closed by owner API',()=>{
 assert.ok(domain.includes("resultSortOrder?:'index-asc'|'index-desc'|'count-asc'|'count-desc'"));
 assert.ok(domain.includes("w.resultSortOrder===undefined||(w.kind==='results-button'"));
});
