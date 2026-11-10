import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('mobile key is conditional on enabled percentages and pie chart with data',()=>{
 assert.ok(ui.includes('chart===\'pie\'&&total>0&&widget.pieShowPercentages===true&&<div className="linked-results-pie-mobile-legend"'));
 assert.ok(ui.includes('role="list" aria-label="Percentuali delle risposte"'));
 assert.ok(ui.includes('className="linked-results-pie-mobile-item" role="listitem"'));
 assert.ok(ui.includes('className="linked-results-pie-mobile-percent">{resultPiePercent(r.share)}</strong>'));
 assert.ok(ui.includes("data-mobile-percent-labels={widget.pieShowPercentages===true?'true':'false'}"));
});
test('each nonzero colored slice gets its original source name, percent and optional number',()=>{
 assert.ok(ui.includes("pieSegments.map(r=><div key={'pie-mobile-'+r.index}"));
 assert.ok(ui.includes('backgroundColor:pieColors[r.index-1]'));
 assert.ok(ui.includes('data[r.index-1]?.label'));
 assert.ok(ui.includes("pieShowOptionNumbers===true?(r.index+'. '):''"));
});
test('CSS exposes mobile legend for all real authoring and phone presentation surfaces',()=>{
 assert.ok(css.includes('grid-template-columns:repeat(auto-fit,minmax(min(100%,145px),1fr))'));
 assert.ok(css.includes('font:750 clamp(14px,.88em,20px)/1.25 Arial,sans-serif'));
 for(const marker of ['@media(max-width:640px)','canvas-editor-group[data-canvas-device="phone"]','audience-widget-layout.stage-phone','rehearsal-phone-stage','rehearsal-phone-widescreen-frame']){
  assert.ok(css.includes(marker),marker);
 }
 assert.ok(css.includes('.linked-results-pie-chart[data-mobile-percent-labels="true"] .linked-results-pie-callout{display:none}'));
});
test('desktop SVG pie leaders and editable radius are still intact',()=>{
 assert.ok(css.includes('.linked-results-pie-chart .linked-results-pie-callout text'));
 assert.ok(ui.includes('data-pie-size={resultPieSize(widget.pieSize)}'));
 assert.ok(ui.includes('className="linked-results-pie-callout"'));
});