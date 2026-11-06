/** RC224: every newly authored widget defaults to Arial; thumbnail actions fit viewports. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {thumbnailMenuPosition} from '../src/thumbnail-menu-layout.ts';
import {initialWidgetTextStyle,widgetTextDefaults} from '../src/widget-typography-defaults.ts';
import {newTitleWidget,newFooterWidget,widgetDisplay} from '../src/slide-master.ts';
import {GRAPHIC_PRESETS,graphicStyle} from '../src/graphic-presets.ts';
import {stageWidgetTypography} from '../src/stage-widget-typography.ts';
import {widgetTypographyStyle} from '../src/widget-appearance.ts';

const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const kinds=['rating','reactions','text','shape','line','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count','title','footer'];

test('all 20 newly inserted page/scheme widget kinds resolve to Arial by default',()=>{
 for(const kind of kinds){
  assert.equal(initialWidgetTextStyle(kind).fontFamily,'Arial',kind);
  assert.equal(widgetTypographyStyle(initialWidgetTextStyle(kind)).fontFamily,'Arial',kind);
  assert.equal(stageWidgetTypography({id:'test',kind,style:initialWidgetTextStyle(kind)},{pageTitle:'Test'}).fontFamily,'Arial',kind);
 }
 assert.match(main,/const schemaWidgetKinds=editorWidgetKinds/);
 assert.match(main,/style:\{\.\.\.initialWidgetTextStyle\(kind\),/);
 assert.match(main,/style:\{\.\.\.initialWidgetTextStyle\(k\),/);
 assert.match(main,/onDrop=\{e=>\{const kind=e\.dataTransfer\.getData\('application\/x-quorivio-widget'\)/);
 assert.match(css,/:is\(\.slide-scheme-workspace,\.powerpoint-editor\) \.widget-canvas-item\{/);
});

test('scheme defaults, master title inheritance and footer all begin in Arial',()=>{
 const title=newTitleWidget('Titolo');
 const footer=newFooterWidget('schema-footer');
 assert.equal(widgetDisplay(title,{pageTitle:'Titolo'}).style.fontFamily,'Arial');
 assert.equal(widgetDisplay(footer,{}).style.fontFamily,'Arial');
 assert.equal(footer.style?.fontFamily,'Arial');
 assert.equal(stageWidgetTypography(title,{pageTitle:'Titolo'}).fontFamily,'Arial');
 assert.equal(stageWidgetTypography(footer,{}).fontFamily,'Arial');
 assert.match(main,/\[newTitleWidget\(snap\.session\.title\),newFooterWidget\('schema-footer'\)\]/);
});

test('saved and explicitly authored fonts are never reset to Arial',()=>{
 const customTitle={...newTitleWidget('Titolo'),style:{fontFamily:'Verdana'}};
 assert.equal(widgetDisplay(customTitle,{masterTitleStyle:{fontFamily:'Georgia'}}).style.fontFamily,'Verdana');
 assert.equal(widgetDisplay(newTitleWidget('Titolo'),{masterTitleStyle:{fontFamily:'Georgia'}}).style.fontFamily,'Georgia');
 assert.equal(widgetTextDefaults('question',{fontFamily:'Tahoma',answerFontFamily:'Georgia'})?.answerFontFamily,'Georgia');
 const customFooter={...newFooterWidget('f'),style:{fontFamily:'Georgia'}};
 assert.equal(widgetDisplay(customFooter,{}).style.fontFamily,'Georgia');
 assert.equal(graphicStyle('shape',GRAPHIC_PRESETS.shape[0]).fontFamily,'Arial');
 assert.equal(graphicStyle('line',GRAPHIC_PRESETS.line[0]).fontFamily,'Arial');
});

test('thumbnail menu stays inside tiny and wide viewports even at bottom right',()=>{
 for(const [width,height] of [[320,240],[390,380],[390,844],[768,500],[1440,900]]){
  for(const [x,y] of [[0,0],[width/2,height/2],[width-1,height-1],[-100,-200]]){
   const pos=thumbnailMenuPosition(x,y,width,height);
   assert.ok(pos.left>=8&&pos.top>=8,JSON.stringify({width,height,x,y,pos}));
   assert.ok(pos.left+Math.min(270,width-16)<=width-8,JSON.stringify({width,height,x,y,pos}));
   assert.ok(pos.top+pos.maxHeight<=height-8,JSON.stringify({width,height,x,y,pos}));
   assert.ok(pos.maxHeight>=Math.min(224,height-16),JSON.stringify({width,height,x,y,pos}));
  }
 }
});

test('thumbnail menu groups all commands in keyboard accessible expandable sections',()=>{
 for(const label of ['Crea e importa pagine','Ordina pagine','Esporta e dati'])assert.ok(main.includes(label));
 for(const label of ['Apri pagina','Rinomina {selectedPageIds.length','Duplica {selectedPageIds.length','Nuova pagina prima','Nuova pagina dopo','Importa PDF/PPTX…','Importa layout JSON','Sposta su','Sposta giù','Esporta layout JSON','Elimina {selectedPageIds.length'])assert.ok(main.includes(label),label);
 assert.match(main,/className="page-editor-thumb-submenu"/);
 assert.match(main,/maxHeight:pageMenuPosition\.maxHeight/);
 assert.match(main,/setPageMenuPosition\(thumbnailMenuPosition\(/);
 assert.match(css,/\.page-editor-thumb-menu-floating \.page-editor-thumb-submenu>summary:focus-visible/);
 assert.match(css,/max-height:var\(--thumbnail-menu-max-height,calc\(100dvh - 16px\)\)!important/);
 assert.match(css,/min-height:0!important;overflow-x:hidden!important;overflow-y:auto!important/);
});
