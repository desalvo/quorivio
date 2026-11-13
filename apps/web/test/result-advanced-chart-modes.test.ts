import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
import {effectiveResultView} from '../src/widget-results.ts';
import {sortedResultBars} from '../src/result-top-rows.ts';
const source={id:'src',kind:'question',label:'Vote',options:[{id:'a',label:'A'},{id:'b',label:'B'},{id:'c',label:'C'}]};
const widget={id:'result',kind:'results-button',targetWidgetId:'src'};
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
test('all four modes resolve when linked and inherit from source when not overridden',()=>{
 for(const resultsView of ['line','area','donut','radar']){
  assert.equal(effectiveResultView({...widget,resultsView},[source]),resultsView);
  assert.equal(effectiveResultView(widget,[{...source,resultsView}]),resultsView);
 }
 assert.equal(effectiveResultView({...widget,resultsView:'invalid'},[source]),'bars');
});
test('sorted chart data uses same source order and anonymous aggregate values',()=>{
 const rows=[{id:'a',label:'A',count:1},{id:'b',label:'B',count:9},{id:'c',label:'C',count:3}];
 assert.deepEqual(sortedResultBars(rows,'count-desc').map(r=>r.id),['b','c','a']);
 assert.deepEqual(sortedResultBars(rows,'index-asc').map(r=>r.id),['a','b','c']);
});
test('both author controls and linked/legacy rendering contain all four options',()=>{
 const m=readFileSync(resolve(root,'apps/web/src/main.tsx'),'utf8');
 for(const type of ['line','area','donut','radar'])assert.ok(m.includes(`<option value="${type}">`),type);
 assert.ok(m.includes('validAdvancedChartKind(chart)'));
 assert.ok(m.includes('validAdvancedChartKind(mode)'));
 assert.ok(m.includes('Donut - Formato widget'));
 assert.ok(m.includes('Livelli griglia radar'));
 assert.ok(m.includes('Opacità area grafico risultati'));
});
