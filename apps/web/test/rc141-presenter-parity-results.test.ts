import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validPageDesign} from '../../api/src/domain.ts';
import {REHEARSAL_EMOJIS,eligibleStatisticSources} from '../src/widget-results.ts';
const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const reaction=readFileSync(new URL('../src/reaction-choices.tsx',import.meta.url),'utf8');
const rating=readFileSync(new URL('../src/rating-choices.tsx',import.meta.url),'utf8');
const api=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');
const root={id:'results',kind:'results-button',targetWidgetId:'q',resultsOnly:true};
test('RC141: only-results is optional, scoped to a result widget and defaults off',()=>{
 assert.equal(validPageDesign({widgets:[{id:'q',kind:'question',answerMode:'text',label:'Domanda'},root]}),true);
 assert.equal(validPageDesign({widgets:[{id:'results',kind:'results-button',resultsOnly:false}]}),true);
 assert.equal(validPageDesign({widgets:[{...root,resultsOnly:'false'}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'rating',kind:'rating',label:'Voto',resultsOnly:true}]}),false);
 assert.match(main,/aria-label="Mostra soltanto i risultati"/);
 assert.match(main,/checked=\{w.resultsOnly===true\}/);
 assert.match(main,/!widget.resultsOnly/);
 assert.deepEqual(eligibleStatisticSources([root,{id:'q',kind:'question'}]).map(w=>w.id),['q']);
});
test('RC141: presenter result counts never separate from their answer, including cloud',()=>{
 assert.match(main,/className="linked-result-pair"/);
 assert.match(main,/className="linked-result-label"/);
 assert.match(css,/\.linked-result-pair\{[\s\S]*?white-space:nowrap!important/);
 assert.match(css,/\.linked-result-pair>output\{[\s\S]*?white-space:nowrap!important/);
 assert.match(css,/\[data-fit-mode="scale"\] \.linked-results-row/);
 assert.match(css,/overflow:visible!important/);
 assert.match(main,/minScale=\{w.kind==='results-button'\?\.005:\.08\}/);
});
test('RC141: editor, presenter and audience share reaction controls',()=>{
 assert.equal(REHEARSAL_EMOJIS.length,8);
 assert.match(reaction,/REHEARSAL_EMOJIS\.map\(emoji/);
 assert.match(reaction,/readOnly\|\|disabled\|\|!onSelect/);
 assert.equal(main.match(/<ReactionChoices\b/g)?.length,3);
 assert.match(main,/w.showTitle!==false&&<strong><WidgetStyledText text=\{w.label\|\|'Reazioni'\}/);
 assert.ok(main.includes("w.kind==='reactions'?{...w,showTitle:false}:w"));
 assert.ok(main.includes("w.kind==='results-button'?{...w,showTitle:editing===w.id?false:w.showTitle}"));
 assert.match(css,/\.reaction-choice-buttons>button\{/);
});
test('RC141: editor uses the same native inputs as presenter and participant for multiple choice',()=>{
 assert.match(main,/name=\{'editor-option-'\+w.id\}/);
 assert.match(main,/w.answerMode==='multiple'\?'checkbox':'radio'/);
 assert.match(main,/q.answerMode==='multiple'\?'checkbox':'radio'/);
 assert.match(css,/\.canvas-widget-answer-preview \.widget-answer-option>input/);
 assert.match(main,/answerOptionStyle\(w.style\)/);
});
test('RC141: participant can replace a rating without duplicate rows; concurrent requests stay guarded',()=>{
 assert.match(api,/ON CONFLICT\(activity_id,participant_id,widget_id\) DO UPDATE SET/);
 assert.match(api,/page_ratings.score IS DISTINCT FROM EXCLUDED.score/);
 assert.match(main,/pendingRatingVotes\.current\.has\(key\)/);
 assert.match(main,/setRatingPending\(old=>\[\.\.\.new Set/);
 assert.match(main,/ratingVotes\[entry\.activity\.id\+':'\+w\.id\]/);
 assert.match(main,/disabled=\{ratingPending\.includes\(w.id\)\}/);
 assert.match(rating,/aria-pressed=\{current===String\(rating\)\}/);
});
