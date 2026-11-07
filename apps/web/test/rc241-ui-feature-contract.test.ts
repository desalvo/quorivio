import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {mobileWidgetHeight,mobileStageHeight,mobilePageWidgets} from '../src/mobile-page-layout.ts';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const format=readFileSync(new URL('../src/result-format-controls.tsx',import.meta.url),'utf8');

test('independent answer labels share typography across the final word but keep a distinct count',()=>{
 assert.match(ui,/className="linked-result-pair" data-result-custom=/);
 assert.match(ui,/className="linked-result-final">\{splitResultLabel\(r\.label\)\.last\}<output>/);
 assert.match(css,/\.linked-result-pair>\.linked-result-final\{[\s\S]*?font-size:inherit!important/);
 assert.match(css,/\.linked-result-final>output\{font-size:inherit!important/);
 assert.match(format,/Independent, persisted formatting/); // user-facing, per-option controls shown in format window
 assert.match(ui,/<details className="palette-ribbon-advanced" open>/);
});

test('phone question page compacts short answers without clipping lengthy options',()=>{
 const small=[{id:'one',kind:'question',options:[{label:'A'},{label:'B'}]}];
 const long=[{id:'one',kind:'question',options:[{label:'A'.repeat(255)},{label:'B'}]}];
 const smallHeight=mobileStageHeight(small);
 assert.ok(smallHeight>=720);
 assert.ok(mobileWidgetHeight(long[0])>mobileWidgetHeight(small[0])+100);
 const manual={positions:{one:{x:10,y:5,width:85,height:40}}};
 assert.equal(mobilePageWidgets(small,manual)[0].position.x,10);
 assert.match(css,/\[data-canvas-device="phone"\] \.widget-canvas-item\{[\s\S]*?padding:10px!important/);
 assert.match(css,/\.rehearsal-phone-stage \.rehearsal-widget\{[\s\S]*?padding:10px!important/);
});

test('presenter single and paired previews share the same 1280x720 stage',()=>{
 assert.match(ui,/function DesktopRehearsalStage/);
 assert.match(ui,/height:720\*scale/);
 assert.match(ui,/width:1280,height:720,transform:`scale\(\$\{scale\}\)`/);
 assert.match(ui,/mode==='presenter'\|\|mode==='both'/);
 assert.match(ui,/<DesktopRehearsalStage>\{renderSlide\('presenter'\)\}<\/DesktopRehearsalStage>/);
 assert.match(css,/\.rehearsal-desktop-stage>\.rehearsal-slide/);
});

test('editor top bar offers functioning cut copy paste info undo and redo controls',()=>{
 for(const part of ['<Scissors size={17}/>','<Copy size={17}/>','<ClipboardPaste size={17}/>','<Info size={17}/>','<Undo2 size={17}/>','<Redo2 size={17}/>'])assert.ok(ui.includes(part),part);
 for(const action of ["issueEditorClipboard('cut')","issueEditorClipboard('copy')","issueEditorClipboard('paste')",'onClick={undoPageWidgets}','onClick={redoPageWidgets}'])assert.ok(ui.includes(action),action);
 assert.match(ui,/toolbarCommand=\{editorToolbarCommand\}/);
 assert.match(ui,/onToolbarClipboardChange=\{setEditorClipboardReady\}/);
 assert.match(ui,/aria-label="Comandi editor pagine"/);
});
