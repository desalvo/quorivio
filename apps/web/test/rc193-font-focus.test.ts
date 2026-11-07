/** RC193: focus is owned by exactly one rich-text field; whole-widget font
 * changes include answer choices and an independently editable numeric size. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {answerOptionStyle} from '../src/widget-answer-style.ts';
import {widgetTypographyStyle} from '../src/widget-appearance.ts';
import {applyAllWidgetTypeface,scaleAllWidgetTypography,styledSegments} from '../src/widget-text-marks.ts';
const editor=readFileSync(new URL('../src/widget-rich-editor.tsx',import.meta.url),'utf8');
const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('stale selection in a previously active option cannot steal the active input after a rerender',()=>{
 assert.match(editor,/const focused=active&&document\.activeElement===el/);
 assert.match(editor,/const selection=focused\?\(domTextRange\(el\)\|\|remembered\.current\):null/);
 assert.match(editor,/if\(focused&&selection\)\{remembered\.current=selection;restoreDomTextRange\(el,selection\)\}/);
 assert.match(editor,/onBlur=\{\(\)=>\{remembered\.current=null\}\}/);
 assert.doesNotMatch(editor,/if\(active&&selection\)restoreDomTextRange/);
});
test('rich editor does not replace unrelated DOM siblings for unchanged rich-text fragments',()=>{
 assert.match(editor,/const signature=JSON\.stringify\(parts\)/);
 assert.match(editor,/renderedSignature\.current===signature&&el\.textContent===value/);
 assert.match(editor,/if\(!el\|\|composing\.current\)return/);
 const pieces=styledSegments('Opzione A',[], 'option:a');
 assert.deepEqual(styledSegments('Opzione A',[{field:'option:b',start:0,end:2,style:{bold:true}}], 'option:a'),pieces);
});
test('default question and answer choices always use Arial, even when old pages have no authored style',()=>{
 const empty=answerOptionStyle();
 assert.equal(empty.fontFamily,'Arial');
 assert.equal(empty['--q-answer-font-family'],'Arial');
 assert.equal(widgetTypographyStyle(undefined).fontFamily,'Arial');
 assert.match(css,/canvas-widget-answer-preview\[data-answer-mode\]\{\s*font-family:var\(--q-answer-font-family,Arial\)!important/);
 assert.match(css,/canvas-subquestion-option\{\s*font-family:var\(--q-answer-font-family,Arial\)!important/);
});
test('whole-widget font updates option font, including independent question marks',()=>{
 const widget={style:{fontFamily:'Arial',fontSize:18,answerFontFamily:'Verdana',answerFontSize:22},textMarks:[{field:'option:a',start:0,end:2,style:{fontFamily:'Verdana'}},{field:'question:q1:option:b',start:0,end:3,style:{fontFamily:'Verdana'}}]};
 const changed=applyAllWidgetTypeface(widget,{fontFamily:'Georgia'});
 assert.equal(changed.style.fontFamily,'Georgia');
 assert.equal(changed.style.answerFontFamily,'Georgia');
 assert.ok(changed.textMarks.every(mark=>mark.style.fontFamily==='Georgia'));
 assert.equal(answerOptionStyle(changed.style).fontFamily,'Georgia');
 const resized=scaleAllWidgetTypography(changed,2);
 assert.equal(resized.style.fontSize,36);
 assert.equal(resized.style.answerFontSize,44);
});
test('numeric font size is editable at all scopes, validates on commit, and offers two real arrow buttons',()=>{
 assert.match(main,/function WidgetFontSizeControl\(/);
 assert.match(main,/value=\{draft\}/);
 assert.match(main,/onChange=\{e=>\{const value=e\.currentTarget\.value;setDraft\(value\);const next=valid\(value\)/);
 assert.match(main,/onBlur=\{\(\)=>\{focused\.current=false;commit\(\)\}\}/);
 assert.match(main,/onApply=\{setSize\}/);
 assert.match(main,/Aumenta dimensione carattere di 1/);
 assert.match(main,/Diminuisci dimensione carattere di 1/);
 assert.ok(!main.includes("effectiveScope==='widget'?<div className=\"palette-ribbon-scale\""));
 assert.match(css,/\.palette-ribbon-font-stepper button/);
});
