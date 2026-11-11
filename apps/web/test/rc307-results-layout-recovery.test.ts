import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {sortedResultBars,visibleResultBars} from '../src/result-top-rows.ts';
import {resultPieLayout} from '../src/result-pie-layout.ts';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const original=[{id:'first',count:8},{id:'second',count:10},{id:'third',count:11}];
test('RC307 all graph types have a single source-ordered data sequence',()=>{
 assert.ok(ui.includes('const data=sortedResultBars(sourceRows,widget.resultSortOrder)'));
 assert.ok(ui.includes('const displayRows=visibleResultBars(sourceRows,widget.resultSortOrder,widget.resultTopCount)'));
 assert.ok(ui.includes('const pieSegments=resultPieLayout(data.map(r=>r.count)'));
 assert.ok(ui.includes('rankedRows={data}'));
 for(const order of ['index-asc','index-desc','count-asc','count-desc']){
  const actual=sortedResultBars(original,order);
  assert.deepEqual(visibleResultBars(original,order,3).map(x=>x.id),actual.map(x=>x.id));
 }
});
test('RC307 pie sorting preserves source option numbering independently of slice order',()=>{
 const source=sortedResultBars(original,'count-desc');
 const nums=source.map(x=>original.findIndex(y=>y.id===x.id)+1);
 const slices=resultPieLayout(source.map(x=>x.count),72,true,true,nums);
 assert.deepEqual(slices.map(x=>x.label.split(' ')[0]),['3.','2.','1.']);
 assert.deepEqual(slices.map(x=>x.count),[11,10,8]);
});
test('RC307 one consistent scroll/no-scale results fit policy for every view',()=>{
 for(const marker of [
  "allowScale={!['qr','participant-count','results-button'].includes(w.kind)}",
  "allowScale={!['qr','participant-count','results-button'].includes(kind)&&!mobile}",
  "allowScale={!['qr','participant-count','results-button'].includes(w.kind)&&!mobileMode&&editing!==w.id}",
 ])assert.ok(ui.includes(marker),marker);
 assert.ok(ui.includes("editor textStyle={stageWidgetTypography(w,{pageTitle,masterTitleStyle},mobileMode)"));
 assert.ok(css.includes('RC307 — One results layout in editor/schema, rehearsal and live projection'));
 assert.ok(css.includes('.canvas-widget-results-native{display:contents!important;}'));
});
test('RC307 results title is not forcibly suppressed in editor rendering',()=>{
 assert.ok(ui.includes("w.kind==='results-button'?{...w,showTitle:editing===w.id?false:w.showTitle}"));
 assert.ok(!ui.includes("['reactions','results-button'].includes(w.kind)?{...w,showTitle:false}"));
 assert.ok(ui.includes("!(w.kind==='results-button'&&(w.resultsOnly===true||editing!==w.id))"));
});
test('RC307 a broken live results component cannot take down presenter workspace',()=>{
 assert.ok(ui.includes('class ResultsWidgetErrorBoundary extends React.Component'));
 assert.ok(ui.includes("La sessione e la dashboard restano operative."));
 assert.ok(ui.includes("<ResultsWidgetErrorBoundary key={'page-'+current.id}"));
 assert.ok(ui.includes('<ResultsWidgetErrorBoundary widgetId={w.id}>'));
 assert.ok(ui.includes('Riprova grafico'));
});
test('RC307 Format widget sort applies to all graphs',()=>{
 assert.ok(ui.includes('Ordinamento risposte (tutti i grafici)'));
 assert.ok(ui.includes('aria-label="Ordinamento risposte risultati"'));
 for(const mode of ['index-asc','index-desc','count-asc','count-desc'])assert.ok(ui.includes('<option value="'+mode+'">'));
});
