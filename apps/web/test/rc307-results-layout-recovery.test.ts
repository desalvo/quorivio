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

test('RC309 malformed live page or legacy statistics cannot unmount the authenticated workspace',()=>{
 assert.ok(ui.includes("<ResultsWidgetErrorBoundary key={'page-'+current.id} widgetId={'page-'+current.id}>"));
 const guarded=ui.split("<ResultsWidgetErrorBoundary key={'page-'+current.id} widgetId={'page-'+current.id}>")[1]?.split('</ResultsWidgetErrorBoundary>')[0]||'';
 assert.ok(guarded.includes('resolveSlideMasterWidgets('),'page title and master widgets are inside the boundary');
 assert.ok(guarded.includes('<PresenterPageResults '),'live projection is inside the boundary');
 assert.ok(ui.includes("<ResultsWidgetErrorBoundary key={'statistics-'+activity.id} widgetId={'statistics-'+activity.id}>"),'the legacy statistics panel has its own boundary');
 assert.ok(ui.includes('La sessione e la dashboard restano operative.'));
});

test('RC309 authenticated dashboard defers live results into a local boundary',()=>{
 assert.ok(ui.includes("function DashboardLiveResults({snapshot,activity,renderResults}"));
 assert.ok(ui.includes("<ResultsWidgetErrorBoundary key={'dashboard-live-'+current.id} widgetId={'dashboard-live-'+current.id}>"));
 assert.ok(ui.includes('<DashboardLiveResults snapshot={snap} activity={current} renderResults={showResults}/>'));
 assert.ok(!ui.includes('{showResults(snap,current)}'),'never execute live-results render within root App reconciliation');
 assert.ok(ui.includes('const results=Array.isArray(s?.results)?s.results:[]'));
 assert.ok(ui.includes('const options=Array.isArray(a?.options)?a.options:[]'));
 assert.ok(ui.includes('Number.isFinite(count)&&count>0?count:0'));
});

// The participant-facing page can differ from the presenter page. Its optional
// discussion widgets must never take down the authenticated dashboard.
test('RC310 independently routed audience extensions stay inside an error boundary',()=>{
 assert.ok(ui.includes("<ResultsWidgetErrorBoundary key={'audience-extension-'+current.id} widgetId={'audience-extension-'+current.id}>"));
 assert.ok(ui.includes('Array.isArray((current as any).page_design?.widgets)'));
 assert.ok(ui.includes('<PresenterAudienceExtensions key={current.id} sessionId={selected} activityId={current.id}/>'));
});

test('RC311 unexpected workspace failure never silently clears the selected session',()=>{
 const boundary=ui.split('class WorkspaceErrorBoundary')[1]?.split('function GlobalPageZoomShell')[0]||'';
 const catchBody=boundary.split('componentDidCatch(error:Error)')[1]?.split('render(){')[0]||'';
 assert.ok(catchBody.includes('this.setState'),'auto recovery attempts one retry');
 assert.ok(!catchBody.includes('writeWorkspaceLocation('),'automatic recovery must keep session identity');
 assert.ok(boundary.includes('Riprova la sessione corrente'));
 assert.ok(boundary.includes('La sessione selezionata è stata conservata.'));
});

test('RC312 bounded pie size 25–150 and empty pie visible',()=>{
 assert.ok(ui.includes("{chart==='pie'&&<svg"));
 assert.ok(ui.includes('className="linked-results-pie-empty"'));
 assert.ok(ui.includes('min={25} max={150} step={5}'));
 assert.ok(css.includes('max-height:42%!important'));
});
test('RC312 page shortcuts cannot intercept widget Backspace',()=>{
 assert.ok(ui.includes("if(action==='delete'&&!focusInThumbnails)return;"));
 assert.ok(ui.includes('e.preventDefault();e.stopPropagation();'));
});
test('RC312 corner QR drag resizes image, side drag retains pixel dimensions',()=>{
 assert.ok(ui.includes("const corner=['nw','ne','sw','se'].includes(g.edge)"));
 assert.ok(ui.includes('const ratio=corner?'));
 assert.ok(ui.includes('qrImagePixels:pixels'));
 assert.ok(css.includes('var(--qr-image-size,100%)'));
});
