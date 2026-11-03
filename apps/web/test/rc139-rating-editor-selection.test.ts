import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const editor=readFileSync(new URL('../src/widget-rich-editor.tsx',import.meta.url),'utf8');
const rating=readFileSync(new URL('../src/rating-choices.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
test('one rating scale is shared in editor, real audience, and split rehearsal',()=>{
 assert.equal(ui.match(/<RatingChoices\b/g)?.length,3);
 assert.match(ui,/\['rating','reactions','results-button'\]\.includes\(w.kind\)\?\{\.\.\.w,showTitle:false\}:w/);
 assert.match(ui,/if\(kind==='rating'\).*widget.showTitle!==false/);
 assert.match(rating,/Array.from\(\{length:11\}/);
 assert.match(rating,/readOnly\|\|disabled\|\|!onSelect/);
});
test('inline caret selection never starts dragging the containing widget',()=>{
 assert.match(ui,/\[contenteditable=true\],\[role=textbox\]/);
 assert.match(ui,/onDoubleClick=\{e=>\{if\(\(e.target as HTMLElement\).closest/);
 assert.match(editor,/onPointerDown=\{e=>\{if\(active\)e.stopPropagation\(\)\}\}/);
 assert.match(editor,/onDoubleClick=\{e=>\{if\(active\)\{e.stopPropagation\(\)/);
 assert.match(css,/\.widget-rich-editing\{user-select:text!important/);
});
test('properties permit native mid-text caret and text drag selection',()=>{
 assert.doesNotMatch(ui,/onDoubleClick=\{e=>e.currentTarget.select\(\)\}/);
 assert.match(ui,/className="slide-master-widget-settings" onPointerDown=/);
});
test('closing format widget does not clear active widget selection',()=>{
 assert.match(ui,/onClick=\{\(\)=>setRibbonDismissed\(true\)\}/);
 assert.match(ui,/active&&!ribbonDismissed&&widgets.some/);
});
test('scale content is not transformed while editing text',()=>{
 assert.match(ui,/allowScale=\{editing!==w.id&&/);
 assert.match(css,/\.widget-fit-content\{min-height:0\}/);
});
