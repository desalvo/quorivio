import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {mobilePageWidgets,mobileStageHeight,mobileWidgetHeight} from '../src/mobile-page-layout.ts';
const ui=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('RC171 desktop/smartphone switch is in the always-visible editor toolbar, before widget rail',()=>{
 const editor=ui.slice(ui.indexOf('<section className="panel powerpoint-editor editor-ux-v2"'));
 const header=editor.indexOf('<header className="editor-mock-header">');
 const slider=editor.indexOf('className="editor-device-switch"');
 const rail=editor.indexOf('className="editor-widget-rail"');
 const stage=editor.indexOf('className="editor-stage"');
 assert.ok(header>=0&&slider>header&&slider<rail&&slider<stage);
 assert.match(editor,/role="switch" aria-label="Modifica layout Smartphone" checked=\{canvasDevice==='phone'\}/);
 assert.match(editor,/Ricompatta automaticamente/);
 assert.match(css,/\.editor-mock-header>\.editor-device-switch/);
});

test('RC171 graphic palette buttons share bounded normal widget wrappers and expose accessible preset trigger',()=>{
 assert.match(ui,/schema\?trigger:<span className="editor-icon-wrapper editor-graphic-wrapper">\{trigger\}/);
 assert.match(ui,/data-graphic-palette=\{kind\}/);
 assert.match(ui,/onContextMenu=\{e=>\{e\.preventDefault\(\);/);
 assert.match(ui,/onPointerDown=\{e=>\{if\(e\.pointerType==='mouse'\)return/);
 assert.match(ui,/aria-label=\{'Scegli tipo e formato: '\+label\}/);
 assert.match(css,/\.editor-widget-grid \.editor-graphic-wrapper\{position:relative;flex:0 0 64px!important/);
 assert.match(css,/\.editor-widget-grid\{display:flex!important;flex-wrap:wrap!important/);
 assert.match(css,/\.editor-graphic-options\{/);
});

test('RC171 auto phone placement packs visible content contiguously, preserving minimum height',()=>{
 const widgets=[
  {id:'q',kind:'question',position:{x:10,y:75,width:50},options:[]},
  {id:'r',kind:'reactions',position:{x:10,y:22,width:50}},
  {id:'t',kind:'title',position:{x:10,y:4,width:50}},
 ];
 const original=JSON.stringify(widgets);
 const height=mobileStageHeight(widgets);
 assert.equal(height,720);
 const positions=mobilePageWidgets(widgets);
 const r=positions.find(w=>w.id==='r')!.position!;
 const t=positions.find(w=>w.id==='t')!.position!;
 const q=positions.find(w=>w.id==='q')!.position!;
 const bottom=(p:typeof q)=>Math.round((p.y+(p.height||0))*height/100);
 const top=(p:typeof q)=>Math.round(p.y*height/100);
 assert.ok(top(r)-bottom(t)<=9,'no phantom gap between title and reactions');
 assert.ok(top(q)-bottom(r)<=9,'no phantom gap between reactions and question');
 assert.ok(top(q)<260,'question stays visible high on mobile viewport instead of far below reactions');
 assert.equal(JSON.stringify(widgets),original,'do not mutate desktop positions');
});

test('RC171 long interactive content grows rather than clipping; explicit custom phone positions preserved',()=>{
 const long=[{id:'title',kind:'title'},
   ...Array.from({length:6},(_,i)=>({id:`q${i}`,kind:'question',options:Array.from({length:4},(_,j)=>({id:String(j)}))})),
   {id:'footer',kind:'footer'}];
 const height=mobileStageHeight(long);
 assert.ok(height>720);
 assert.ok(mobileWidgetHeight(long[1])>=300);
 const fixed={x:14,y:43,width:75,height:22,rotation:0};
 const placed=mobilePageWidgets(long,{positions:{q1:fixed}});
 assert.deepEqual(placed.find(w=>w.id==='q1')!.position,fixed);
 const footer=placed.find(w=>w.kind==='footer')!.position!;
 assert.ok(footer.y+footer.height!<=100&&footer.y>90);
});

test('RC171 editing an existing graphic has right-click type/width/fill controls without a misleading title command',()=>{
 assert.match(ui,/className="canvas-context-graphic-options"/);
 assert.match(ui,/Preset grafico del widget selezionato/);
 assert.match(ui,/Spessore grafico nel menu contestuale/);
 assert.match(ui,/Riempimento forma nel menu contestuale/);
 assert.match(ui,/w\.kind!=='line'&&w\.kind!=='shape'/);
});
