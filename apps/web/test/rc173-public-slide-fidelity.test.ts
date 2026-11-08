import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {participantVisibleWidgets,participantPhoneLayout} from '../src/live-slide-policy.ts';

const ui=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const participant=ui.slice(ui.indexOf('{joinPath?<main id="main-content"'),ui.indexOf('publicPath?<PresenterLiveScreen'));

const pos=(x:number,y:number,width=35,height=20)=>({x,y,width,height,rotation:0});

test('RC173 result widgets and their exact unlabelled background fills leave no audience footprint',()=>{
 const authored=[
  {id:'title',kind:'title',label:'Page',position:pos(5,5,80,12)},
  {id:'result-fill',kind:'shape',label:'',position:pos(45,30)},
  {id:'result',kind:'results-button',position:pos(45,30)},
  {id:'unrelated',kind:'shape',label:'',position:pos(0,0,100,100)},
  {id:'text-decoration',kind:'shape',label:'Decorazione',position:pos(45,30)},
  {id:'rating',kind:'rating',position:pos(5,60)},
 ];
 const visible=participantVisibleWidgets(authored);
 assert.deepEqual(visible.map(w=>w.id),['title','unrelated','text-decoration','rating']);
 assert.deepEqual(participantPhoneLayout(authored).widgets.map(w=>w.id),visible.map(w=>w.id));
 assert.deepEqual(authored[1].position,pos(45,30),'do not mutate the page or presenter layout');
});

test('RC173 participant page paints the authored background once (stage only), not on the page wrapper',()=>{
 assert.match(participant,/style=\{\{backgroundColor:"transparent",backgroundImage:"none"\}\}/);
 // RC265: stage backgrounds are composed with optional phone geometry and
 // an explicit imported full-canvas background; the former bare ternary
 // branch is no longer present. The authored image still paints on stage only.
 assert.match(participant,/\.\.\.slideBackgroundCss\(entry\.activity\.page_design,entry\.theme,/);
 assert.equal((participant.match(/slideBackgroundCss\(entry\.activity\.page_design/g)||[]).length,1,'participant stage must paint its authored background exactly once');
 assert.doesNotMatch(participant,/participant-live-view" style=\{window\.matchMedia/);
 assert.match(css,/main\.participant-live-view\{background-image:none!important;background-color:transparent!important\}/);
});

test('RC173 accessible reading is a separate linear white document, while manually selected phone layout overrides automatic resizing',()=>{
 assert.match(participant, /participantReadingMode\?\{backgroundImage:"none",backgroundColor:"#ffffff",backgroundSize:"auto"\}/);
 assert.match(participant,/aria-pressed=\{participantReadingMode\} onClick=\{\(\)=>\{setParticipantModeExplicit\(true\);setParticipantReadingMode\(true\);setParticipantPhoneMode\(false\)\}\}>Lettura accessibile/);
 assert.match(participant,/onClick=\{\(\)=>\{setParticipantModeExplicit\(true\);setParticipantReadingMode\(false\);setParticipantPhoneMode\(true\)\}\}>Layout smartphone/);
 assert.match(ui,/const audiencePortrait=joinPath&&participantPhoneLayoutEnabled\(participantPhoneMode,participantReadingMode,participantModeExplicit,entry\?\.activity\)/);
 assert.match(css,/stage-reading\{\s*background:#fff!important;background-image:none!important/);
 assert.match(css,/stage-reading>\.page-widget:is\(\[data-widget-kind="shape"\],\[data-widget-kind="line"\]\)\{display:none!important\}/);
});

test('RC173 16:9 smartphone keeps saved geometry and removes mobile minimum touch-size distortions',()=>{
 assert.match(css,/main\.participant-live-view \.audience-widget-layout\.stage-fidelity>\.page-widget\{\s*position:absolute!important;left:var\(--stage-x\)!important;top:var\(--stage-y\)!important;/);
 assert.match(css,/main\.participant-live-view \.audience-widget-layout\.stage-fidelity :is\(button,select,input,textarea\)\{\s*min-width:0!important;min-height:0!important/);
 assert.match(participant,/aria-pressed=\{!participantReadingMode&&!audiencePortrait\}/);
 assert.match(participant,/audiencePortrait\?audiencePhoneLayout\.widgets:participantReadingMode\?audienceReadingWidgets:audienceVisibleWidgets/);
});

test('RC173 editor owns a single rating title, with one editable field during text editing',()=>{
 assert.match(ui,/!\(w\.kind==='rating'&&editing!==w\.id\)&&<RichWidgetText/);
 assert.match(ui,/w\.kind==='rating'\?\{\.\.\.w,showTitle:editing===w\.id\?false:w\.showTitle\}/);
 assert.match(ui,/if\(kind==='rating'\)return <RatingStageContent widget=\{widget\} readOnly\/>/);
});

test('RC173 no results fallback appears for a public non-widget activity',()=>{
 assert.doesNotMatch(participant,/<h3>Risultati live<\/h3>/);
 assert.doesNotMatch(participant,/<PresenterLinkedResult/);
});
