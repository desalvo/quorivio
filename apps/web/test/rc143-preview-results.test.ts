import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {topResultRows,splitResultLabel} from '../src/result-top-rows.ts';
import {phoneStageScale,PHONE_STAGE_WIDTH,PHONE_STAGE_HEIGHT} from '../src/rehearsal-phone-scale.ts';
import {validPageDesign} from '../../api/src/domain.ts';

test('RC143 result rank: first five descending with stable tie order and bounded configurable count',()=>{
 const rows=[{id:'a',label:'Alpha',count:4},{id:'b',label:'Beta',count:10},{id:'c',label:'Gamma',count:5},{id:'d',label:'Delta',count:8},{id:'e',label:'Epsilon',count:6},{id:'f',label:'Zeta',count:8}];
 assert.deepEqual(topResultRows(rows).map(x=>x.id),['b','d','f','e','c']);
 assert.deepEqual(topResultRows(rows,2).map(x=>x.id),['b','d']);
 assert.deepEqual(topResultRows(rows,21).map(x=>x.id),['b','d','f','e','c']);
 assert.equal(rows[0].id,'a','ranking must never sort original live rows in place');
});
test('RC143 result labels keep last word with numeric count while allowing earlier line breaks',()=>{
 assert.deepEqual(splitResultLabel('Infrastrutture di calcolo'),{prefix:'Infrastrutture di ',last:'calcolo'});
 assert.deepEqual(splitResultLabel('Servizi'),{prefix:'',last:'Servizi'});
 const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
 assert.match(css,/\.linked-results \.linked-results-row \.linked-result-pair\{[\s\S]*?white-space:normal!important/);
 assert.match(css,/\.linked-results \.linked-results-row \.linked-result-pair>\.linked-result-final\{[\s\S]*?white-space:nowrap!important/);
});
test('RC144 390px phone stage retains legible type and scales only within its frame',()=>{
 assert.equal(PHONE_STAGE_WIDTH,390);assert.equal(PHONE_STAGE_HEIGHT,720);
 assert.equal(phoneStageScale(390),1);
 assert.equal(phoneStageScale(195),.5);
 assert.equal(phoneStageScale(1920),1);
 const src=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 assert.ok(src.includes("renderSlide('participant',true)"));
 assert.ok(src.includes('rehearsal-phone-stage'));
 const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
 assert.ok(css.includes('.rehearsal-phone-stage .rehearsal-widgets'));
 assert.ok(css.includes('position:absolute!important;left:var(--stage-x)!important'));
});
test('RC143 results top count is accepted only for results widgets, 1..20',()=>{
 const base={id:'a',kind:'results-button',label:'Results',position:{x:0,y:0,width:50,height:50}};
 const good={widgets:[{...base,resultTopCount:5}]};
 assert.equal(validPageDesign(good),true);
 assert.equal(validPageDesign({widgets:[{...base,resultTopCount:20}]}),true);
 assert.equal(validPageDesign({widgets:[{...base,resultTopCount:0}]}),false);
 assert.equal(validPageDesign({widgets:[{...base,resultTopCount:21}]}),false);
 assert.equal(validPageDesign({widgets:[{...base,resultTopCount:5.2}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'b',kind:'text',resultTopCount:5}]}),false);
});
test('RC143 formatting ribbon has a visible close control and scroll-safe wrapping',()=>{
 const src=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 assert.ok(src.includes('setRibbonDismissed(true)'));
 assert.ok(src.includes('aria-label="Chiudi Formato widget"'));
 const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
 assert.ok(css.includes('flex-wrap:wrap!important;align-content:flex-start!important'));
 assert.ok(css.includes('overflow-x:hidden!important;overflow-y:auto!important'));
});
