import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {newTitleWidget} from '../src/slide-master.ts';
import {stageWidgetTypography} from '../src/stage-widget-typography.ts';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('RC169 inherited master title font is identical in public and rehearsal phone stages',()=>{
 const widget=newTitleWidget('Page');
 const master={fontFamily:'Georgia',fontSize:38,color:'#112233',bold:true};
 const first=stageWidgetTypography(widget,{pageTitle:'Page',masterTitleStyle:master},true);
 const second=stageWidgetTypography(widget,{pageTitle:'Page',masterTitleStyle:master},true);
 assert.deepEqual(first,second);
 assert.equal(first.fontSize,'38px');
 assert.equal(first['--mobile-widget-font-size'],'38px');
 assert.equal(first.fontFamily,'Georgia');
 assert.equal(first.color,'#112233');
 assert.equal(first.fontWeight,'bold');
 const desktop=stageWidgetTypography(widget,{pageTitle:'Page',masterTitleStyle:master});
 assert.equal(desktop.fontSize,`${(38/1280*100).toFixed(5)}cqw`);
 assert.equal(desktop['--mobile-widget-font-size'],undefined);
 assert.equal(widget.style?.fontSize,undefined,'master resolution must not mutate saved widget');
});

test('RC169 direct title style and phone-custom style override master, not other way round',()=>{
 const master={fontSize:42,fontFamily:'Georgia'};
 const title={...newTitleWidget('Page'),style:{fontFamily:'Arial',fontSize:27}};
 assert.equal(stageWidgetTypography(title,{masterTitleStyle:master},true).fontSize,'27px');
 assert.equal(stageWidgetTypography(title,{masterTitleStyle:master},true).fontFamily,'Arial');
 const custom={...title,style:{...title.style,fontSize:31,fontFamily:'Verdana'}};
 assert.equal(stageWidgetTypography(custom,{masterTitleStyle:master},true).fontSize,'31px');
 assert.equal(stageWidgetTypography({...title,titleUseMaster:false,style:{}},{masterTitleStyle:master},true).fontSize,'24px');
});

test('RC169 rating content has one shared implementation in all four rendering routes',()=>{
 const anchor='function RatingStageContent(';const start=ui.indexOf(anchor);
 assert.ok(start>0);
 const body=ui.slice(start,ui.indexOf('/** The exact same chart',start));
 for(const required of ['widgetTitleVisible(widget)','widget.description','WidgetStyledText','RatingCommentField','rating-range-hint','RatingChoices','size={widget.style?.ratingButtonSize}'])assert.ok(body.includes(required),required);
 assert.match(ui,/if\(kind==='rating'\)return <RatingStageContent widget=\{widget\} readOnly\/>/);
 assert.match(ui,/kind==='rating'\?<RatingStageContent widget=\{w\} readOnly=\{viewer==='presenter'\}/);
 assert.match(ui,/w.kind==='rating'\?<RatingStageContent widget=\{w\} comment=\{ratingComments\[w.id\]/);
 assert.equal(ui.match(/RatingCommentField /g)?.length,1,'no duplicate editor/live comment input');
 assert.doesNotMatch(ui,/canvas-rating-preview/);
 assert.doesNotMatch(ui,/<strong>\{w.label\|\|'Indice di gradimento'\}<\/strong>/);
});

test('RC169 both real and rehearsal stages use the same master-aware typography, and phone previews allow widget overflow',()=>{
 assert.match(ui,/stageWidgetTypography\(w,\{pageTitle:viewActivity.title,masterTitleStyle:snapshot.session.theme\?\.master\?\.titleStyle\},mobile\)/);
 assert.match(ui,/stageWidgetTypography\(w,\{pageTitle:entry.activity.title,masterTitleStyle:entry.theme\?\.master\?\.titleStyle\},audiencePortrait\)/);
 assert.doesNotMatch(ui,/mobile\?\{fontSize:`\$\{w.style\?\.fontSize\|\|16\}px`/);
 assert.match(css,/\.rehearsal-phone-stage \.rehearsal-widget\{\s*font-size:var\(--mobile-widget-font-size,16px\)!important;padding:10px!important;overflow:auto!important;/);
 assert.match(css, /\.audience-widget-layout\.stage-phone>\.page-widget\{[\s\S]*?overflow:auto!important;/);
});
