import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resultPieLayout,resultPieSize,resultPiePercent,PIE_VIEWBOX} from '../src/result-pie-layout.ts';
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const api=readFileSync(new URL('../../api/src/domain.ts',import.meta.url),'utf8');

test('pie sizing is bounded and defaults safely for legacy sessions',()=>{
 assert.equal(resultPieSize(undefined),72);
 assert.equal(resultPieSize(NaN),72);
 assert.equal(resultPieSize(10),40);
 assert.equal(resultPieSize(120),100);
 assert.equal(resultPieSize(65),65);
});
test('pie percentages preserve tiny nonzero slices without rounding to zero',()=>{
 assert.equal(resultPiePercent(.0002),'0.02%');
 assert.equal(resultPiePercent(.0125),'1.3%');
});
test('full-circle pie has two valid arc segments and one readable percentage',()=>{
 const [s]=resultPieLayout([100],100,true);
 assert.equal(s.label,'100%');
 assert.match(s.path,/ A .* A .* Z$/);
 assert.ok(s.leader.includes(','));
});
test('each nonzero slice receives a distinct outside label and leader',()=>{
 const parts=resultPieLayout([50,40,9.98,.02,0],65,true,true);
 assert.equal(parts.length,4);
 assert.deepEqual(parts.map(p=>p.index),[1,2,3,4]);
 assert.equal(parts.at(-1)?.label,'4. 0.02%');
 assert.ok(parts.every(p=>p.labelX<100||p.labelX>400));
 assert.ok(parts.every(p=>p.leader.split(' ').length===3));
});
test('12 labels avoid collisions even for highly skewed pies',()=>{
 for(const counts of [Array(12).fill(1),[1000,...Array(11).fill(1)]]){
  const parts=resultPieLayout(counts,100,true,true);
  assert.equal(parts.length,12);
  for(const side of ['left','right']){
   const ys=parts.filter(p=>p.side===side).map(p=>p.labelY).sort((a,b)=>a-b);
   assert.ok(ys.every(y=>y>=18&&y<=PIE_VIEWBOX.height-18));
   for(let i=1;i<ys.length;i++)assert.ok(ys[i]-ys[i-1]>=19,`overlapping labels ${ys}`);
  }
 }
});
test('R preserves identical base and graded border box, without moving verdict icons',()=>{
 assert.match(css,/\.linked-results \.linked-source-answers \.widget-answer-option,\s*\.linked-results \.linked-results-items \.linked-results-row,/);
 assert.match(css,/border:3px solid transparent!important/);
 assert.match(css,/\.linked-results \.linked-source-answers \.widget-answer-option\[data-answer-verdict\]\{\s*padding-right:/);
 assert.match(css,/position:absolute!important;display:inline-flex!important/);
 assert.match(ui,/setTruthVisible\(v=>!v\)/);
});
test('result view uses SVG leaders and independently configurable circle radius',()=>{
 assert.match(ui,/className="linked-results-pie linked-results-pie-chart"/);
 assert.match(ui,/className="linked-results-pie-callout"/);
 assert.match(ui,/<polyline points=\{r\.leader\}/);
 assert.match(ui,/aria-label="Dimensione torta risultati"/);
 assert.match(ui,/pieSize:Number\(e\.target\.value\)/);
});
test('API accepts only 40-100 integer percent for results widget',()=>{
 assert.match(api,/pieSize\?:number/);
 assert.match(api,/w\.kind==='results-button'&&Number\.isInteger\(w\.pieSize\)&&w\.pieSize>=40&&w\.pieSize<=100/);
});
