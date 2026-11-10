import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const oldBrowser=readFileSync(new URL('../../../tools/ci_rc296_mobile_pie_chromium.py',import.meta.url),'utf8');

test('desktop pie percentage list is accessible, not display:none',()=>{
 const start=css.indexOf('.linked-results .linked-results-pie-mobile-legend{');
 assert.ok(start>0);
 const block=css.slice(start,css.indexOf('}',start));
 assert.ok(block.includes('display:grid'));
 assert.ok(!/^\s*display:none\s*;/m.test(block));
 assert.ok(block.includes('position:absolute'));
 assert.ok(block.includes('clip-path:inset(50%)'));
 assert.ok(block.includes('width:1px;height:1px'));
});

test('each percentage listitem conveys exact source, count, and percentage',()=>{
 assert.ok(ui.includes('role="list" aria-label="Percentuali delle risposte"'));
 assert.ok(ui.includes('className="linked-results-pie-mobile-item" role="listitem" aria-label={'));
 assert.ok(ui.includes("data[r.index-1]?.label||('Opzione '+r.index)"));
 assert.ok(ui.includes("r.count===1?'risposta':'risposte'"));
 assert.ok(ui.includes('resultPiePercent(r.share)'));
});

test('the SVG no longer claims to show percentages when hidden',()=>{
 assert.ok(ui.includes('widget.pieShowPercentages===true?"Distribuzione percentuale delle risposte"'));
 assert.ok(ui.includes(':"Distribuzione delle risposte"'));
 assert.ok(ui.includes('chart===\'pie\'&&total>0&&widget.pieShowPercentages===true'));
});

test('phone restores visible layout and RC296 checks effective visual state',()=>{
 assert.ok(css.includes('display:grid;position:static;width:100%;height:auto;margin:0;'));
 assert.ok(css.includes('overflow:visible;clip-path:none;white-space:normal;'));
 assert.ok(css.includes('audience-widget-layout.stage-phone'));
 assert.ok(oldBrowser.includes("getComputedStyle(legend).clipPath==='none'"));
});
