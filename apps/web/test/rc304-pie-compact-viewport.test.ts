
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {PIE_VIEWBOX,resultPieLayout,resultPieViewport} from '../src/result-pie-layout.ts';
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');

test('RC304 reducing size releases vertical room for text even without labels',()=>{
 const heights=[100,72,40].map(size=>resultPieViewport(resultPieLayout([21,39,40],size,false,false),size).height);
 assert.ok(heights[0]>heights[1]&&heights[1]>heights[2],JSON.stringify(heights));
 assert.ok(heights[0]<PIE_VIEWBOX.height&&heights[2]<PIE_VIEWBOX.height/2);
});
test('RC304 callouts remain inside tight viewport across 1 to 12 categories',()=>{
 for(const values of [[21,39,40],[100],[1000,...Array(11).fill(1)],Array(12).fill(1)]){
  for(const size of [40,65,72,100]){
   const slices=resultPieLayout(values,size,true,true);
   const box=resultPieViewport(slices,size),radius=116*size/100;
   assert.ok(box.y<=PIE_VIEWBOX.cy-radius);
   assert.ok(box.y+box.height>=PIE_VIEWBOX.cy+radius);
   for(const s of slices){
    assert.ok(box.y<=s.labelY-12&&box.y+box.height>=s.labelY+12);
    const elbow=PIE_VIEWBOX.cy+Math.sin(s.midAngle)*(radius+12);
    assert.ok(box.y<=elbow&&box.y+box.height>=elbow);
   }
   assert.ok(box.height<=PIE_VIEWBOX.height);
  }
 }
});
test('RC304 hiding labels yields an SVG closely hugging the circle',()=>{
 const slices=resultPieLayout([10,20,30],40,false,false);
 assert.ok(slices.every(s=>s.label===''));
 const box=resultPieViewport(slices,40);
 assert.ok(box.height>=2*116*.4&&box.height<=2*116*.4+12);
});
test('RC304 JSX and every responsive CSS rule use the dynamic aspect ratio',()=>{
 assert.ok(ui.includes('resultPieViewport(pieSegments,widget.pieSize)'));
 assert.ok(ui.includes('data-pie-viewport-height={pieViewport.height}'));
 assert.ok(ui.includes('viewBox={`0 ${pieViewport.y} ${pieViewport.width} ${pieViewport.height}`}'));
 assert.ok(css.includes('aspect-ratio:var(--pie-chart-ratio,500 / 320)!important'));
 assert.ok(!css.includes('aspect-ratio:500 / 320!important'));
});
