import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {scaleWidgetFont,styledSegments} from '../src/widget-text-marks.ts';
import {pageCountdownSeconds,pageInteractionExpired} from '../src/rehearsal-timer.ts';
import {rehearsalFreeTextRows} from '../src/widget-results.ts';
import {validPageDesign} from '../../api/src/domain.ts';
const source=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
test('widget-wide typography scaling preserves independent marks, colors and font family',()=>{
 const widget={style:{fontSize:20},textMarks:[
  {field:'label',start:0,end:4,style:{fontSize:30,color:'#ff0000',fontFamily:'Georgia'}},
  {field:'description',start:0,end:2,style:{fontSize:12,color:'#008800',bold:true}},
  {field:'label',start:5,end:8,style:{italic:true}}]};
 const changed=scaleWidgetFont(widget,40);
 assert.equal(changed.style.fontSize,40);
 assert.deepEqual(changed.textMarks.map(m=>m.style.fontSize),[60,24,undefined]);
 assert.equal(changed.textMarks[0].style.fontFamily,'Georgia');
 assert.equal(changed.textMarks[0].style.color,'#ff0000');
 assert.equal(changed.textMarks[1].style.bold,true);
 assert.equal(widget.textMarks[0].style.fontSize,30);
 assert.equal(styledSegments('Title here',changed.textMarks,'label')[0].style.fontSize,60);
});
test('font scaling respects bounded API schema and never discards marks',()=>{
 const widget={style:{fontSize:32},textMarks:[{field:'label',start:0,end:2,style:{fontSize:80,color:'#ffffff'}}]};
 assert.equal(scaleWidgetFont(widget,64).textMarks[0].style.fontSize,96);
 assert.deepEqual(scaleWidgetFont(widget,0).textMarks,widget.textMarks);
});
test('timer duration is configurable up to sixty minutes only on timer widgets',()=>{
 for(const seconds of [1,60,600,3600])assert.equal(validPageDesign({widgets:[{id:'timerA',kind:'timer',durationSeconds:seconds}]}),true);
 for(const seconds of [0,-1,3601,1.5])assert.equal(validPageDesign({widgets:[{id:'timerA',kind:'timer',durationSeconds:seconds}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'quizA',kind:'timed-quiz',durationSeconds:3600}]}),false);
 assert.match(source,/Durata massima countdown del widget/);
});
test('one deadline gates every action; changing preview modes cannot reset expiry',()=>{
 assert.equal(pageCountdownSeconds([]),undefined);
 assert.equal(pageInteractionExpired([],1000,900000),false);
 const widgets=[{kind:'timer',durationSeconds:20},{kind:'timer',durationSeconds:15},{kind:'question'}];
 assert.equal(pageCountdownSeconds(widgets),15);
 assert.equal(pageInteractionExpired(widgets,1000,15999),false);
 assert.equal(pageInteractionExpired(widgets,1000,16000),true);
 assert.match(source,/pageInteractionExpired\(widgets,pageStartedAt,Date.now\(\)\)/);
 assert.match(source,/disabled=\{pageExpired\}/);
});
test('participant count is private and rehearsal uses labelled simulated value',()=>{
 assert.match(source,/data-simulated-participants/);
 assert.match(source,/w\.kind!=='participant-count'/);
 assert.match(source,/viewer==='presenter'\|\|!\['results-button','participant-count'\]/);
});
test('free-text presenter rehearsal includes committed answer while retaining fixtures',()=>{
 const sourceWidget={id:'freeText',kind:'question',answerMode:'text'};
 const original=rehearsalFreeTextRows(sourceWidget,{});
 assert.equal(original.length,2);
 const draft=rehearsalFreeTextRows(sourceWidget,{});
 assert.deepEqual(draft,original);
 const sent=rehearsalFreeTextRows(sourceWidget,{freeText:'Risposta effettivamente inviata'});
 assert.equal(sent.length,3);
 assert.equal(sent[2].label,'Risposta effettivamente inviata');
 assert.equal(sent[2].count,1);
});
test('geometry interaction handles extend beyond the selected widget clip',()=>{
 assert.match(css,/widget-canvas-item\[data-selected="true"\]\{clip-path:none!important/);
 assert.match(css,/widget-rotate-handle\{visibility:visible/);
});
