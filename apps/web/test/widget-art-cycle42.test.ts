import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validPageDesign,validWidgetTextStyle} from '../../api/src/domain.ts';
import {widgetArtData,widgetHasAuthoredFill,widgetTimerFace} from '../src/widget-art.ts';
import {widgetAppearanceStyle} from '../src/widget-appearance.ts';

test('three timer faces survive validated page-design persistence',()=>{
 for(const face of ['hourglass','dial','digital'] as const){
  for(const kind of ['timer','timed-quiz'] as const){
   assert.equal(validPageDesign({widgets:[{id:'timer_one',kind,style:{artTheme:'glass',artEffect:'glow',timerFace:face}}]}),true);
   assert.equal(widgetTimerFace({timerFace:face}),face);
  }
 }
 assert.equal(validWidgetTextStyle({timerFace:'url(javascript:evil)'}),false);
 assert.equal(validWidgetTextStyle({timerFace:42}),false);
 assert.equal(widgetTimerFace(undefined),'hourglass');
 assert.equal(widgetTimerFace({timerFace:'url(x)' as any}),'hourglass');
});

test('opacity and transparent custom fills never allow decorative gradients through',()=>{
 for(const style of [{fillOpacity:0},{fillOpacity:0.4},{fillOpacity:1},{fillMode:'solid' as const},{fillNone:true},{fillColor:'#123456'}]){
  assert.equal(widgetHasAuthoredFill(style),true);
  assert.equal(widgetArtData(style)['data-art-custom-fill'],'true');
  const appearance=widgetAppearanceStyle(style);
  assert.equal(appearance.backgroundImage,'none');
 }
 assert.equal(widgetAppearanceStyle({fillOpacity:0}).backgroundColor,'#ffffff00');
 assert.equal(widgetAppearanceStyle({fillOpacity:0.4}).backgroundColor,'#ffffff66');
 assert.equal(widgetAppearanceStyle({fillOpacity:1}).backgroundColor,'#ffffff');
 assert.equal(widgetAppearanceStyle({fillNone:true}).backgroundColor,'transparent');
 assert.equal(widgetAppearanceStyle({fillMode:'image',fillImageAssetId:'5fc9370c-2b80-4c8d-8098-613734b95ee0'},'/api/image').backgroundImage,'url("/api/image")');
 assert.match(String(widgetAppearanceStyle({fillMode:'gradient',fillOpacity:.4}).backgroundImage),/^linear-gradient/);
 assert.equal(widgetArtData({strokeColor:'#102030'})['data-art-custom-fill'],'false');
});

test('timer faces are shared by projected, rehearsal, live participant and editor preview',()=>{
 const src=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
 assert.match(src,/aria-label="Quadrante grafico timer"/);
 assert.match(src,/data-timer-face=\{face\}/);
 assert.match(src,/data-timer-face=\{widgetTimerFace\(w.style\)\}/);
 assert.ok((src.match(/face=\{widgetTimerFace\((?:w|widget)\.style\)\}/g)||[]).length>=6);
 for(const face of ['dial','digital'])assert.ok(css.includes(`[data-timer-face="${face}"]`));
 assert.match(css,/prefers-reduced-motion:reduce/);
});
