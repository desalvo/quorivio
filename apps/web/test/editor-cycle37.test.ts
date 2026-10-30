import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {contextMenuCoordinates} from '../src/editor-context-menu.ts';
import {questionModeOptions,invalidPageWidgetReason} from '../src/editor-save-safety.ts';
import {widgetTypographyStyle} from '../src/widget-appearance.ts';
import {validPageDesign} from '../../api/src/domain.ts';

test('white canvas defaults to black without overriding a chosen text color',()=>{
 assert.equal(widgetTypographyStyle(undefined).color,'#000000');
 assert.equal(widgetTypographyStyle({color:'#c300a0'}).color,'#c300a0');
});
test('menu is placed in viewport rather than within the small widget',()=>{
 assert.deepEqual(contextMenuCoordinates(430,270,450,300),{x:202,y:8});
 assert.deepEqual(contextMenuCoordinates(20,20,1440,900),{x:20,y:20});
 assert.deepEqual(contextMenuCoordinates(Number.NaN,Number.NaN,1440,900),{x:8,y:8});
});
test('multiple-choice poll with two options has valid authoritative page design',()=>{
 const choices=questionModeOptions([],'multiple');
 assert.deepEqual(choices.map(o=>o.label),['Opzione A','Opzione B']);
 const design={header:'Domanda',widgets:[{id:'widget_1',kind:'question',label:'Sondaggio',answerMode:'multiple',options:choices,correctOptionIds:[],position:{x:4,y:4,width:45,height:25,rotation:0}}]};
 assert.equal(validPageDesign(design),true);
 assert.equal(invalidPageWidgetReason(design),undefined);
 assert.equal(invalidPageWidgetReason({widgets:[{kind:'question',answerMode:'multiple',options:[choices[0]]}]}),'Il sondaggio richiede almeno due opzioni di risposta.');
});
test('switching modes preserves pre-existing IDs and avoids collisions',()=>{
 const original=[{id:'choice_a',label:'Uno'}];
 const next=questionModeOptions(original,'multiple');
 assert.equal(next[0].id,'choice_a');
 assert.equal(new Set(next.map(o=>o.id)).size,2);
 assert.equal(questionModeOptions(next,'single'),next);
});
test('menu uses body portal and rehearsal has a closable error boundary',()=>{
 const source=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 assert.match(source,/contextWidget===w\.id&&createPortal\(<div className="canvas-context-menu"/);
 assert.match(source,/>Elimina<\/button><\/div>,document\.body\)/);
 assert.match(source,/class RehearsalErrorBoundary/);
 assert.match(source,/Chiudi anteprima e torna all'editor/);
 assert.match(source,/!validPageDesign\(question\)\|\|!validPageDesign\(result\)/);
});
