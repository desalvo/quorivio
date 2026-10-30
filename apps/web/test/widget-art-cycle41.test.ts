import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {widgetArtData,widgetArtEffect,widgetArtTheme,widgetHasAuthoredFill} from '../src/widget-art.ts';
import {widgetAppearanceStyle} from '../src/widget-appearance.ts';
import {validPageDesign,validWidgetTextStyle} from '../../api/src/domain.ts';

test('art themes and effects persist in the server-validated page design',()=>{
 for(const artTheme of ['studio','glass','playful','minimal'] as const){
  for(const artEffect of ['none','float','glow','tilt'] as const){
   assert.equal(validPageDesign({widgets:[{id:'timer_one',kind:'timer',label:'Tempo',style:{artTheme,artEffect}}]}),true);
   assert.deepEqual(widgetArtData({artTheme,artEffect}),{'data-art-theme':artTheme,'data-art-effect':artEffect,'data-art-custom-fill':'false'});
  }
 }
 assert.equal(validPageDesign({widgets:[{id:'timer_one',kind:'timer',style:{artTheme:'evil'}}]}),false);
 assert.equal(validWidgetTextStyle({artEffect:'javascript:alert(1)'}),false);
});
test('unknown legacy or corrupted values fall back safely without accepting CSS injection',()=>{
 assert.equal(widgetArtTheme(undefined),'studio');
 assert.equal(widgetArtEffect(undefined),'none');
 assert.equal(widgetArtTheme({artTheme:'url(https://evil.invalid)' as any}),'studio');
 assert.equal(widgetArtEffect({artEffect:'transform:rotate(45deg)' as any}),'none');
});
test('hand-authored gradients, images, colors, transparency override decorative art',()=>{
 for(const style of [{fillNone:true},{fillColor:'#123456'},{fillMode:'gradient' as const},{fillMode:'image' as const}]){
  assert.equal(widgetHasAuthoredFill(style),true);
  assert.equal(widgetArtData(style)['data-art-custom-fill'],'true');
 }
 assert.equal(widgetHasAuthoredFill({}),false);
 assert.equal(widgetAppearanceStyle({fillNone:true}).backgroundColor,'transparent');
 assert.equal(widgetAppearanceStyle({fillMode:'gradient',fillColor:'#123456',gradientEndColor:'#abcdef'}).backgroundImage?.toString().includes('linear-gradient'),true);
});
test('shared art data are wired into editor, rehearsal, presenter, and audience views',()=>{
 const src=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 const calls=src.match(/\{\.\.\.widgetArtData\(w\.style\)\}/g)||[];
 assert.equal(calls.length,4);
 assert.match(src,/aria-label="Tema artistico del widget"/);
 assert.match(src,/aria-label="Effetto artistico del widget"/);
 assert.match(src,/widget-timer-design-preview/);
 const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
 assert.match(css,/data-art-custom-fill="true"/);
 assert.match(css,/prefers-reduced-motion:reduce/);
 assert.match(css,/data-art-effect="tilt"/);
 assert.match(css,/data-art-theme="minimal"/);
});
