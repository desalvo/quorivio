import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import {slideBackground,slideBackgroundCss} from '../src/master-background.ts';
import {GRAPHIC_PRESETS,graphicStyle} from '../src/graphic-presets.ts';
import {newTitleWidget,newFooterWidget,widgetDisplay} from '../src/slide-master.ts';
import {widgetTypographyStyle} from '../src/widget-appearance.ts';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const svg=readFileSync(new URL('../src/widget-graphic.tsx',import.meta.url),'utf8');
const server=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');

test('RC161 master background is inherited, local image has priority and phone background is independent',()=>{
 const master=randomUUID(),local=randomUUID();
 const theme={master:{backgroundAssetId:master}};
 assert.deepEqual(slideBackground({},theme),{assetId:master});
 assert.deepEqual(slideBackground({backgroundColor:'#ffffff'},theme),{assetId:master});
 assert.deepEqual(slideBackground({backgroundAssetId:local},theme),{assetId:local});
 assert.deepEqual(slideBackground({backgroundUrl:'https://example.com/slide.png'},theme),{url:'https://example.com/slide.png'});
 assert.deepEqual(slideBackground({},{}),{});
 assert.equal(slideBackgroundCss({},theme,id=>`/assets/${id}`).backgroundImage,`url("/assets/${master}")`);
 assert.match(ui,/canvasDevice==='phone'\?mobileLayoutDraft\.backgroundAssetId\|\|'':slideBackground\(/);
 assert.match(ui,/mobile\?\.backgroundAssetId/);
});
test('RC161 Arial is the effective default for title/footer and unchanged custom master font is respected',()=>{
 const title=newTitleWidget('test'),footer=newFooterWidget('footer');
 assert.equal(widgetTypographyStyle(widgetDisplay(title,{pageTitle:'Title'}).style).fontFamily,'Arial');
 assert.equal(widgetTypographyStyle(footer.style).fontFamily,'Arial');
 assert.equal(widgetTypographyStyle(widgetDisplay(title,{pageTitle:'Title',masterTitleStyle:{fontFamily:'Georgia',fontSize:52}}).style).fontFamily,'Georgia');
 assert.match(css,/\.slide-scheme-workspace,.powerpoint-editor/);
 assert.match(css,/font-family:Arial,sans-serif/);
});
test('RC161 graphic presets cover arrow terminals, dashes, common shapes and editable fills',()=>{
 assert.ok(GRAPHIC_PRESETS.line.length>=8);
 assert.ok(GRAPHIC_PRESETS.shape.length>=10);
 assert.ok(GRAPHIC_PRESETS.line.some(p=>p.style.lineArrow==='both'));
 assert.ok(GRAPHIC_PRESETS.line.some(p=>p.style.lineArrow==='start'));
 assert.ok(GRAPHIC_PRESETS.line.some(p=>p.style.lineArrow==='end'));
 assert.ok(GRAPHIC_PRESETS.line.some(p=>p.style.strokeDash==='dash'));
 assert.ok(GRAPHIC_PRESETS.shape.some(p=>p.style.shapeType==='star'));
 const dashed=GRAPHIC_PRESETS.line.find(p=>p.id==='dash')!;
 assert.equal(graphicStyle('line',dashed,{strokeWidth:4,strokeColor:'#112233',fillColor:'#abcdef',fillNone:false}).strokeDash,'dash');
 assert.equal(graphicStyle('line',dashed,{strokeWidth:4,strokeColor:'#112233',fillColor:'#abcdef',fillNone:false}).strokeWidth,4);
 const withFill=graphicStyle('shape',GRAPHIC_PRESETS.shape[3],{strokeWidth:3,strokeColor:'#445566',fillColor:'#fedcba',fillNone:false});
 assert.equal(withFill.fillColor,'#fedcba');assert.equal(withFill.fillNone,false);
 assert.equal(graphicStyle('shape',GRAPHIC_PRESETS.shape[3],{strokeWidth:3,strokeColor:'#445566',fillColor:'#fedcba',fillNone:true}).fillNone,true);
 assert.match(svg,/markerStart/);assert.match(svg,/markerEnd/);
});
test('RC161 graphics insert on context/right click, long touch, keyboard and remain editable',()=>{
 assert.match(ui,/function GraphicInsertTool\(/);
 assert.match(ui,/onContextMenu=\{e=>\{e\.preventDefault\(\)/);
 assert.match(ui,/setTimeout\(\(\)=>\{suppressClick\.current=true;show\(e\.clientX,e\.clientY\)\},560\)/);
 assert.match(ui,/e\.key==='ContextMenu'/);
 assert.match(ui,/GRAPHIC_PRESETS\[kind\]\.map\(preset/);
 assert.match(ui,/kind:GraphicKind/);
 assert.match(ui,/onInsert=\{\(preset,options\)=>/);
 assert.match(ui,/Terminali freccia/);
 assert.match(ui,/Tipo forma grafica/);
 assert.match(ui,/setSchemaWidgets/);
 assert.match(ui,/setPageWidgets/);
});
test('RC161 lines and shapes have no title in either canvas or projection',()=>{
 assert.match(ui,/if\(kind==='shape'\|\|kind==='line'\)return null/);
 assert.match(ui,/!\['line','shape'\]\.includes\(w\.kind\)/);
 assert.match(css,/widget-rich/);
});
test('RC161 master image upload, persistence, read permission and deletion protection are explicit',()=>{
 assert.match(ui,/async function uploadSchemaBackground\(file:File\|undefined\)/);
 assert.match(ui,/schemaBackgroundAsset/);
 assert.match(ui,/backgroundAssetId:schemaBackgroundAsset/);
 assert.match(server,/s\.theme\?\.master\?\.backgroundAssetId===req\.params\.assetId/);
 assert.match(server,/asset_in_use_by_background/);
});
