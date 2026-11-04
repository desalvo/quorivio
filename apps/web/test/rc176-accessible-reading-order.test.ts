import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {participantReadingWidgets,participantPhoneLayout,participantVisibleWidgets} from '../src/live-slide-policy.ts';

const sample=[
 {id:'footer',kind:'footer',position:{x:0,y:93,width:100,height:7}},
 {id:'count',kind:'participant-count',position:{x:75,y:75,width:15,height:12}},
 {id:'right',kind:'rating',position:{x:70,y:30,width:20,height:20}},
 {id:'fill',kind:'shape',label:'Forma',position:{x:10,y:20,width:40,height:20}},
 {id:'chart',kind:'results-button',position:{x:10,y:20,width:40,height:20}},
 {id:'left',kind:'question',position:{x:20,y:30,width:40,height:20}},
 {id:'headline',kind:'title',position:{x:10,y:8,width:80,height:12}},
 {id:'line',kind:'line',position:{x:10,y:50,width:80,height:1}},
 {id:'topic',kind:'topic-question',position:{x:20,y:70,width:60,height:20}}
];

test('Accessible document order follows authored geometry, with footer last in DOM, not CSS only',()=>{
 assert.deepEqual(participantReadingWidgets(sample).map(w=>w.id),['headline','left','right','topic','footer']);
});

test('The accessible plan removes graphical decoration and private/result backing, without changing the 16:9 and phone widget population',()=>{
 const original=sample.map(w=>w.id);
 const fidelity=participantVisibleWidgets(sample).map(w=>w.id);
 assert.deepEqual(fidelity,['footer','right','left','headline','line','topic']);
 assert.deepEqual(participantPhoneLayout(sample).widgets.map(w=>w.id),fidelity);
 assert.deepEqual(sample.map(w=>w.id),original,'ordering must not mutate the saved source');
});

test('Stable ordering for same-position widgets preserves the widget IDs and never drops nondecorative widgets',()=>{
 const widgets=[
  {id:'d',kind:'text',position:{x:15,y:30,width:30}},
  {id:'c',kind:'text',position:{x:15,y:30,width:30}},
  {id:'a',kind:'title',position:{x:10,y:0,width:80}},
  {id:'b',kind:'question',position:{x:50,y:30,width:30}}
 ];
 assert.deepEqual(participantReadingWidgets(widgets).map(w=>w.id),['a','d','c','b']);
});

test('Live React switches all three independent DOM populations explicitly',()=>{
 const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 assert.match(ui,/const audienceReadingWidgets=participantReadingWidgets\(audienceAuthoredWidgets\)/);
 assert.match(ui,/audiencePortrait\?audiencePhoneLayout\.widgets:participantReadingMode\?audienceReadingWidgets:audienceVisibleWidgets/);
});
