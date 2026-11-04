import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {mobilePageWidgets,mobileStageHeight,mobileWidgetHeight} from '../src/mobile-page-layout.ts';

const ui=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const ratings=fs.readFileSync(new URL('../src/rating-choices.tsx',import.meta.url),'utf8');
function participantView(s:string){
 const start=s.indexOf('{joinPath?<main id="main-content"');
 const end=s.indexOf('publicPath?<PresenterLiveScreen',start);
 assert.ok(start>=0&&end>start,'participant route is present');
 return s.slice(start,end);
}
test('RC160 the live participant slide mounts only authored question/reaction widgets',()=>{
 const view=participantView(ui);
 assert.doesNotMatch(view,/<AudienceExtensions\b/);
 assert.doesNotMatch(view,/className="reaction-bar"/);
 assert.doesNotMatch(view,/Pagina informativa: nessuna risposta richiesta/);
 assert.match(view,/w\.kind==='question'\?<QuestionWidget/);
 assert.match(view,/w\.kind==='topic-question'\?<TopicQuestionWidget/);
 assert.match(view,/w\.kind==='reactions'\?<div className="projection-sample-reactions"/);
 assert.match(view,/\(entry\.activity\.page_design\?\.widgets\|\|\[\]\)\.length\|\|entry\.activity\.type==='slide'\?null/);
});
test('RC160 optional rating comment is the same shared component in editor, previews and live',()=>{
 const view=participantView(ui);
 assert.match(view,/<RatingStageContent widget=\{w\} comment=\{ratingComments\[w\.id\]/);
 assert.match(ui,/if\(kind==='rating'\)return <RatingStageContent widget=\{widget\} readOnly\/>/);
 assert.match(ui,/function RatingStageContent\(/);
 assert.match(ui,/RatingCommentField value=\{comment\}/);
 assert.doesNotMatch(ui,/canvas-rating-preview/);
 assert.match(ui,/demoRatingComments\[w\.id\]/);
 assert.match(ratings,/className="rating-comment-input"/);
 assert.match(css,/textarea\.rating-comment-input\{[\s\S]*?background-color:#ffffff!important/);
 assert.match(css,/color-scheme:light!important/);
});
test('RC160 automatic phone footer is last AND at the bottom even when authored first',()=>{
 const widgets=[
  {id:'footer',kind:'footer'},
  {id:'title',kind:'title'},
  {id:'question',kind:'question'},
  {id:'rating',kind:'rating'},
 ];
 assert.ok(mobileWidgetHeight(widgets[3])>=230,'rating must fit comment and ten choices');
 const stageHeight=mobileStageHeight(widgets);
 const placed=mobilePageWidgets(widgets);
 assert.deepEqual(placed.map(w=>w.id),widgets.map(w=>w.id));
 const footer=placed[0].position!;
 const lastContent=placed[3].position!;
 assert.ok(footer.y>lastContent.y+lastContent.height!);
 assert.ok(footer.y+footer.height!>90,'footer stays at the bottom of the 720px stage');
 assert.ok(footer.y+footer.height!<=100);
 assert.ok(stageHeight>=720);
});
test('RC160 explicit phone footer placement remains author-controlled',()=>{
 const widgets=[{id:'footer',kind:'footer'},{id:'title',kind:'title'}];
 const custom={x:3,y:80,width:94,height:12,rotation:0};
 assert.deepEqual(mobilePageWidgets(widgets,{positions:{footer:custom}})[0].position,custom);
});
test('RC160 reading view places footer and page number after all content widgets',()=>{
 assert.match(css,/\.audience-widget-layout\.stage-reading>\.page-widget\[data-widget-kind="footer"\]\s*\{\s*order:9999!important/);
 assert.match(css,/\.audience-widget-layout\.stage-reading>\.slide-canvas-page-number\{\s*order:10000!important/);
});
