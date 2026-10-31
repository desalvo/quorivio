import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {widgetArtData} from '../src/widget-art.ts';
import {widgetAppearanceStyle} from '../src/widget-appearance.ts';
const web=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
test('transparent and square new widget defaults preserve explicit effects',()=>{
 assert.equal(widgetAppearanceStyle(undefined).backgroundColor,'transparent');
 assert.equal(widgetAppearanceStyle({shapeType:'rectangle',rounded:true}).borderRadius,0);
 assert.equal(widgetArtData(undefined)['data-art-theme'],'plain');
 assert.equal(widgetArtData({artTheme:'glass',artEffect:'glow'})['data-art-effect'],'glow');
 assert.match(web,/style:\{fillNone:true,shapeType:'rectangle'\}/);
 assert.match(css,/quorivio-floating-shadow/);
});
test('dashboard uses continuous layout and real presenter connection HTTP backup',()=>{
 assert.match(web,/session-detail-layout session-tab-/);
 assert.match(css,/\.session-detail-layout>div\{display:contents\}/);
 assert.match(web,/setLiveFallback\(true\)/);
 assert.doesNotMatch(web,/\['results','Monitoraggio live'\]/);
});
test('countdowns offer keep or erase while secure role still owns action',()=>{
 assert.match(web,/clear_responses:clearResponses/);
 assert.match(web,/MANTENENDO le risposte/);
 assert.match(web,/'participant-count':<Gauge size=\{21\}/);
});
