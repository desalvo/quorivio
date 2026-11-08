import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {boundFloatingPosition,boundFloatingSize,floatingLogicalViewport,FLOATING_GRAB_WIDTH,FLOATING_GRAB_HEIGHT} from '../src/editor-floating-geometry.ts';

const root=new URL('../src/',import.meta.url);
const main=readFileSync(new URL('main.tsx',root),'utf8');
const css=readFileSync(new URL('style.css',root),'utf8');

test('RC266 floating palette can reach right and bottom viewport edges without losing the title bar',()=>{
 const viewport={width:1440,height:900};
 const dock=boundFloatingPosition(5000,5000,860,290,viewport.width,viewport.height);
 assert.equal(dock.left,1440-FLOATING_GRAB_WIDTH);
 assert.equal(dock.top,900-FLOATING_GRAB_HEIGHT);
 assert.ok(dock.left>1440-860,'old full-width clamp would stop the window halfway');
 assert.ok(dock.top>900-290,'old full-height clamp would stop the window too early');
 assert.deepEqual(boundFloatingPosition(-5000,-5000,860,290,1440,900),{left:FLOATING_GRAB_WIDTH-860,top:8});
});

test('RC266 floating window can resize within available viewport at desktop and mobile sizes',()=>{
 assert.deepEqual(boundFloatingSize(560,410,1440,900,'properties'),{width:560,height:410});
 assert.deepEqual(boundFloatingSize(5000,5000,390,844,'palette'),{width:374,height:828});
 assert.deepEqual(boundFloatingSize(20,20,390,844,'palette'),{width:320,height:115});
 assert.deepEqual(boundFloatingSize(999,999,280,220,'properties'),{width:264,height:204});
 assert.deepEqual(boundFloatingSize(100,100,280,220,'properties'),{width:264,height:160});
});

test('RC266 retains title-only dragging, accessible corner resize and native text field editing',()=>{
 assert.match(main,/closest\('\.palette-ribbon-head,\.editor-drawer-heading'\)/);
 assert.match(main,/closest\('button,input,textarea,select,a,\[contenteditable=true\]'\)/);
 assert.match(main,/closest\('\.editor-floating-resize-handle'\)/);
 assert.match(main,/onPointerDown=\{start\} onPointerMove=\{move\}/);
 assert.match(main,/onKeyDown=\{resizeWithKeyboard\}/);
 assert.match(main,/setSize\(boundFloatingSize\(/);
 assert.match(css,/width:var\(--editor-floating-width,min\(860px,calc\(100vw - 16px\)\)\)!important/);
 assert.match(css,/\.editor-ux-v2 \.editor-context-drawer\.editor-floating-panel\{\s*width:var\(--editor-floating-width/);
 assert.match(css,/\.editor-floating-panel>\.editor-floating-resize-handle\{/);
});

test('RC266 floating geometry accounts for the global editor CSS zoom',()=>{
 // With html { zoom:80% } the 1440x900 physical viewport becomes a
 // 1800x1125 logical viewport. A fixed panel uses logical coordinates.
 const vp=floatingLogicalViewport(1440,900,0.8);
 assert.deepEqual(vp,{width:1800,height:1125});
 const dock=boundFloatingPosition(5000,5000,860,290,vp.width,vp.height);
 assert.equal(dock.left,1688);
 assert.equal(dock.top,1081);
 assert.ok(dock.left*0.8>1300,'right-docked title remains near physical right edge');
 assert.ok(dock.top*0.8>850,'bottom-docked title remains near physical bottom edge');
 assert.match(main,/floatingLogicalViewport\(window\.innerWidth,window\.innerHeight,Number\.parseFloat\(getComputedStyle\(document\.documentElement\)\.zoom\)\)/);
 assert.match(main,/observer\?\.observe\(document\.documentElement\)/);
});
