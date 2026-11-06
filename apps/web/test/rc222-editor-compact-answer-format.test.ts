/** RC222: answer options in the editor must wrap and obey whole-widget Arial/font changes. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {widgetTextDefaults} from '../src/widget-typography-defaults.ts';
import {answerOptionStyle} from '../src/widget-answer-style.ts';
import {applyAllWidgetTypeface} from '../src/widget-text-marks.ts';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

const options=['option:a','question:sub1:option:b'];
test('legacy answer choices default to Arial for both main and independent questions',()=>{
 for(const kind of ['question','timed-quiz']){
  const defaults=widgetTextDefaults(kind,{});
  assert.equal(answerOptionStyle(defaults).fontFamily,'Arial');
  assert.equal(answerOptionStyle(defaults)['--q-answer-font-family'],'Arial');
 }
 assert.match(ui,/data-answer-mode=\{w\.answerMode\|\|'single'\} style=\{answerOptionStyle\(widgetTextDefaults\(w\.kind,w\.style\)\)\}/);
 assert.match(ui,/className="canvas-subquestion-option" style=\{answerOptionStyle\(widgetTextDefaults\(w\.kind,w\.style\)\)\}/);
});
test('whole-widget font replaces answer font and existing inline overrides, without dropping selected text formatting',()=>{
 const w={style:{fontFamily:'Verdana',answerFontFamily:'Tahoma',fontSize:22,answerFontSize:16},textMarks:options.map(field=>({field,start:0,end:7,style:{fontFamily:'Tahoma',bold:true}}))};
 const next=applyAllWidgetTypeface(w,{fontFamily:'Georgia'});
 assert.equal(next.style.fontFamily,'Georgia');
 assert.equal(next.style.answerFontFamily,'Georgia');
 assert.equal(answerOptionStyle(next.style).fontFamily,'Georgia');
 assert.ok(next.textMarks.every(mark=>mark.style.fontFamily==='Georgia'&&mark.style.bold===true));
 assert.match(ui,/const effectiveScope=selectedRange&&selectedRange\.end>selectedRange\.start\?/);
 assert.match(ui,/const activeTextField=effectiveScope==='widget'\?null:/);
 assert.match(ui,/if\(typographic\)\{patch\(w\.id,applyAllWidgetTypeface\(w,changes as InlineStyle\)\);return;\}/);
});
test('editor rich-text glyph spans can wrap and cannot be truncated by legacy generic span selector',()=>{
 assert.match(css,/\.canvas-widget-answer-preview\[data-answer-mode\]>.widget-answer-option>.widget-rich-inline>span/);
 assert.match(css,/\.canvas-subquestion-option>.widget-rich-inline>span/);
 assert.match(css,/display:inline!important;align-items:baseline!important;white-space:inherit!important/);
 assert.match(css,/white-space:pre-wrap!important;overflow-wrap:anywhere!important;/);
 assert.match(css,/font-family:var\(--q-answer-font-family,Arial\)!important/);
});
test('format ribbon is compact, per-result typography remains accessible on demand',()=>{
 assert.match(ui,/<details className="palette-ribbon-advanced"><summary>Testi indipendenti…<\/summary>/);
 assert.match(ui,/Schede Formato widget/);
 assert.match(css,/body \.editor-floating-panel\.widget-selection-palette \.palette-ribbon-group-title\{\s*display:none!important/);
 assert.match(css,/body \.editor-floating-panel\.widget-selection-palette \.palette-ribbon-group label\{\s*min-height:0!important/);
 assert.match(css,/@media\(max-width:520px\)\{\s*body \.editor-floating-panel\.widget-selection-palette \.palette-ribbon-groups\{\s*flex-wrap:nowrap!important/);
});
