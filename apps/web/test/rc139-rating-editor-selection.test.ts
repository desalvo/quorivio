import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const editor=readFileSync(new URL('../src/widget-rich-editor.tsx',import.meta.url),'utf8');
const rating=readFileSync(new URL('../src/rating-choices.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
test('one rating scale is shared in editor, real audience, and split rehearsal',()=>{
 // One component supplies the ten voting choices and one comment field.
 // Canvas mounts this read-only component through ProjectionWidgetContent,
 // rather than duplicating a second comment outside the widget body.
 assert.equal(ui.match(/<RatingChoices\b/g)?.length,1);
 assert.equal(ui.match(/<RatingCommentField\b/g)?.length,1);
 assert.match(ui,/function RatingStageContent\(/);
 assert.match(ui,/if\(kind==='rating'\)return <RatingStageContent widget=\{widget\} readOnly\/>/);
 assert.match(ui,/kind==='rating'\?<RatingStageContent widget=\{w\} readOnly=\{viewer==='presenter'\}/);
 assert.match(ui,/w.kind==='rating'\?<RatingStageContent widget=\{w\} comment=\{ratingComments\[w.id\]/);
 assert.doesNotMatch(ui,/canvas-rating-preview/);
 assert.match(ui,/w.kind==='rating'\?\{\.\.\.w,showTitle:editing===w.id\?false:w.showTitle\}/);
 assert.match(ui,/widgetTitleVisible\(widget\)/);
 assert.match(rating,/RATING_VALUES\.map\(rating=>/);
 assert.match(readFileSync(new URL('../src/rating-range.ts',import.meta.url),'utf8'),/RATING_MAX=9/);
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
 assert.match(ui,/active&&!ribbonDismissed&&!suspendFormattingRibbon&&widgets\.some/);
 assert.match(ui,/suspendFormattingRibbon=\{pageConflict\}/);
});
test('scale content is not transformed while editing text',()=>{
 assert.ok(ui.includes("allowScale={!['qr','participant-count','results-button'].includes(w.kind)&&!mobileMode&&editing!==w.id}"));
 assert.match(css,/\.widget-fit-content\{min-height:0\}/);
});
