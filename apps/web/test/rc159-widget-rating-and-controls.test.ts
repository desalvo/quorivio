import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
const root=new URL('../src/',import.meta.url);
const main=readFileSync(new URL('main.tsx',root),'utf8');
const css=readFileSync(new URL('style.css',root),'utf8');
const rating=readFileSync(new URL('rating-choices.tsx',root),'utf8');

test('session lifecycle buttons carry distinct semantic classes',()=>{
 for(const [action,color] of [['terminate','#ad2939'],['pause','#b9f4ce'],['reset','#b5e9ff']]){
  assert.match(main,new RegExp('session-action-'+action));
  assert.ok(css.includes('button.session-action-'+action+'{background:'+color));
 }
 assert.match(main,/session-action-terminate" onClick=\{\(\)=>changeStatus\('closed'\)\}/);
 assert.match(main,/session-action-pause" onClick=\{\(\)=>changeStatus\('paused'\)\}/);
});
test('shared optional rating comment is rendered in editor, presenter, rehearsal and real participant',()=>{
 assert.match(main,/import \{RatingChoices,RatingCommentField\} from '\.\/rating-choices\.js'/);
 assert.doesNotMatch(main,/canvas-rating-preview/);
 assert.match(main,/function RatingStageContent\(/);
 assert.match(main,/if\(kind==='rating'\)return <RatingStageContent widget=\{widget\} readOnly\/>/);
 assert.match(main,/widgetTitleVisible\(widget\).*WidgetStyledText text=\{widget.label\|\|'Gradimento'\}/);
 assert.match(main,/demoRatingComments\[w\.id\]/);
 assert.match(main,/comment=\{ratingComments\[w\.id\]\|\|''\} disabled=\{ratingPending.includes\(w.id\)\}/);
 assert.match(main,/RatingCommentField value=\{comment\}/);
 assert.match(rating,/maxLength=\{1000\}/);
 assert.match(rating,/readOnly=\{readOnly\|\|!onChange\}/);
 assert.match(rating,/aria-label="Commento facoltativo"/);
});
test('all rating textareas are white with dark ink on all surfaces',()=>{
 assert.match(css,/\.rating-comment-field \.rating-comment-input\{[^}]*background:#ffffff!important;color:#142b44!important/);
 assert.match(css,/\.rating-comment-field \.rating-comment-input:read-only\{opacity:1/);
 assert.match(css,/\.rating-comment-field \.rating-comment-input:focus-visible/);
});
test('participant and preview question submit buttons have only the label Invia risposta',()=>{
 assert.doesNotMatch(main,/>Invia risposta al widget<|>Invia risposta di prova</);
 assert.match(main,/>Invia risposta<\/button>/);
 assert.match(main,/projection-readonly-submit[^>]*>Invia risposta<\/button>/);
});
