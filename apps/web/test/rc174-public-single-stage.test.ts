import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {participantVisibleWidgets,participantPhoneLayout} from '../src/live-slide-policy.ts';

const ui=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const publicScreen=ui.slice(ui.indexOf('{joinPath?<main id="main-content"'),ui.indexOf('publicPath?<PresenterLiveScreen'));

test('RC174 active joined slide has no duplicate visual session branding outside stage',()=>{
 assert.match(ui,/const participantSlideActive=!!\(joinPath&&joined&&entry\?\.session\?\.status==='active'&&entry\?\.activity\)/);
 assert.match(publicScreen,/\{!participantSlideActive&&\(entry\?\.theme\?\.logos\|\|\[\]\)\.map/);
 assert.match(publicScreen,/className=\{participantSlideActive\?"participant-session-heading-offscreen":undefined\}/);
 assert.match(css,/participant-session-heading-offscreen\{[\s\S]*?clip-path:inset\(50%\)!important/);
 assert.match(css,/participant-live-view\.participant-slide-active>\.panel\{[\s\S]*?background:transparent!important/);
});

test('RC174 joining and paused states retain the session brand and accessible h1',()=>{
 assert.match(publicScreen,/\{!participantSlideActive&&\(entry\?\.theme\?\.logos\|\|\[\]\)\.map/);
 assert.match(publicScreen,/<h1 className=\{participantSlideActive\?"participant-session-heading-offscreen":undefined\}>\{entry\?\.session\?\.title/);
 assert.match(publicScreen,/entry\?\.session\?\.status!=='active'/);
});

test('RC174 legacy media outside the canvas cannot duplicate an authored widget slide',()=>{
 assert.match(publicScreen,/\{!audienceAuthoredWidgets\.length&&\(entry\.activity\.page_design\?\.media\|\|\[\]\)\.map/);
 assert.match(publicScreen,/\{\(audiencePortrait\?audiencePhoneLayout\.widgets:participantReadingMode\?audienceReadingWidgets:audienceVisibleWidgets\)\.map/);
});

test('RC174 faithful narrow 16:9 stage uses proportionally sized labels and form controls',()=>{
 assert.match(css,/main\.participant-live-view \.audience-widget-layout\.stage-fidelity>\.page-widget label\{[\s\S]*?font-size:1\.015625cqw!important/);
 assert.match(css,/main\.participant-live-view \.audience-widget-layout\.stage-fidelity>\.page-widget :is\(textarea,input,select\)\{[\s\S]*?padding:\.9375cqw 1\.09375cqw!important/);
 assert.match(css,/main\.participant-live-view \.audience-widget-layout\.stage-fidelity>\.page-widget button:not\(\.rating-choice-buttons > button\)/);
 assert.match(css,/\.stage-reading\{[\s\S]*?background:#fff!important;background-image:none!important/);
});

test('RC174 participant policy still filters presenter-only widgets before phone geometry',()=>{
 const widgets=[
  {id:'q',kind:'question',position:{x:10,y:20,width:40,height:35}},
  {id:'r',kind:'results-button',position:{x:60,y:20,width:25,height:30}},
  {id:'n',kind:'participant-count',position:{x:80,y:10,width:15,height:10}},
  {id:'f',kind:'footer',position:{x:10,y:90,width:80,height:5}},
 ];
 assert.deepEqual(participantVisibleWidgets(widgets).map(w=>w.id),['q','f']);
 assert.deepEqual(participantPhoneLayout(widgets).widgets.map(w=>w.id),['q','f']);
 assert.deepEqual(widgets.map(w=>w.id),['q','r','n','f']);
});
