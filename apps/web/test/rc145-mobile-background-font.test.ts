import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {widgetTypographyStyle} from '../src/widget-appearance.ts';
import {inlineMarkCss,styledSegments} from '../src/widget-text-marks.ts';

const source=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const section=(start:string,end:string)=>source.slice(source.indexOf(start),source.indexOf(end,source.indexOf(start)));

test('RC145 newly uploaded smartphone backdrop affects mobile state only',()=>{
 const upload=section('async function uploadBackground(', 'async function deleteAsset(');
 assert.match(upload,/if\(forMobile\)\{setMobileLayoutDraft\(old=>\(\{\.\.\.old,backgroundAssetId:applied\.id\}\)\);\}/);
 assert.match(upload,/else if\(forResults\)\{setResultBackgroundAsset\(applied\.id\)/);
 assert.match(upload,/else\{setQuestionBackgroundAsset\(applied\.id\)/);
 assert.match(source,/onBackgroundUpload=\{file=>uploadBackground\(file,false,canvasDevice==='phone'\)\}/);
 assert.match(source,/backgroundAssetId=\{canvasDevice==='phone'\?mobileLayoutDraft\.backgroundAssetId\|\|'':slideBackground\(/);
 assert.match(source,/slideBackground\(\{backgroundAssetId:questionBackgroundAsset\|\|undefined,backgroundUrl:questionBackground\|\|undefined\},snap\.session\.theme\)/);
});

test('RC145 choosing a phone-only solid color replaces its image, never touches desktop background',()=>{
 assert.match(source,/onBackgroundColorChange=\{color=>setMobileLayoutDraft\(old=>\(\{\.\.\.old,backgroundColor:color,backgroundAssetId:undefined\}\)\)\}/);
 assert.match(source,/mobileMode&&<label>Colore di sfondo smartphone/);
 assert.match(css,/\.canvas-editor-group\[data-canvas-device="phone"\] \.canvas-with-rulers \.widget-canvas\{/);
 assert.match(css,/background-color:var\(--editor-phone-background-color,#ffffff\)!important/);
 assert.match(source,/\"--editor-page-background\":backgroundAssetId&&sessionId\?/);
 assert.match(source,/backgroundImage:activity\?\.page_design\?\.mobile\?\.backgroundAssetId\?/);
});

test('RC145 selecting library image uses the smartphone target without unreachable duplicate branch',()=>{
 const select=section('function selectLibraryBackground(', 'async function uploadBackground(');
 assert.equal(select.match(/if\(forMobile\)/g)?.length,1);
 assert.match(select,/if\(forMobile\)setMobileLayoutDraft\(old=>\(\{\.\.\.old,backgroundAssetId:applied\.id\}\)\);/);
 assert.match(source,/selectLibraryBackground\(id,false,true\)/);
});

test('RC145 Arial default, whole-widget overrides and rich-text marks use the same face in editor/projection',()=>{
 assert.equal(widgetTypographyStyle(undefined).fontFamily,'Arial');
 assert.equal(widgetTypographyStyle({fontFamily:'Arial',fontSize:24}).fontFamily,'Arial');
 assert.equal(widgetTypographyStyle({fontFamily:'Georgia',fontSize:24}).fontFamily,'Georgia');
 assert.equal(inlineMarkCss({fontFamily:'Arial'}).fontFamily,'Arial');
 const parts=styledSegments('Arial Georgia',[{field:'label',start:6,end:13,style:{fontFamily:'Georgia'}}],'label');
 assert.deepEqual(parts.map(x=>x.style.fontFamily),[undefined,'Georgia']);
 assert.match(source,/\.\.\.widgetTypographyStyle\(w\.kind==='title'\?widgetDisplay\(w,\{pageTitle,masterTitleStyle\}\)\.style:w\.style\)/);
 assert.match(css,/\.editor-ux-v2 \.widget-canvas-item \.widget-fit-content>\.widget-rich-inline\{\s*font-family:inherit!important;/);
});
