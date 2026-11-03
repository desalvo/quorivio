import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const ribbon=/active&&!ribbonDismissed&&!suspendFormattingRibbon&&widgets\.some\(w=>w\.id===active\)/;
const conflictWire=/suspendFormattingRibbon=\{pageConflict\}/;

function ribbonContracts(text:string){
 return ribbon.test(text) && conflictWire.test(text)
  && /suspendFormattingRibbon=false/.test(text)
  && /onClick=\{\(\)=>setRibbonDismissed\(true\)\}/.test(text);
}

test('RC155 selected-widget ribbon is suspended only during an editor revision conflict',()=>{
 assert.ok(ribbonContracts(source));
 assert.match(source,/pageConflict&&<div className="editor-secondary-workflow"/);
 assert.match(source,/onClick=\{\(\)=>void inspectPageConflict\(\)\}/);
});

test('RC155 regression: removing conflict suspension from ribbon is rejected',()=>{
 const broken=source.replace('!suspendFormattingRibbon&&','');
 assert.notEqual(broken,source);
 assert.equal(ribbonContracts(broken),false);
});

test('RC155 regression: disconnecting page conflict from editor canvas is rejected',()=>{
 const broken=source.replace('suspendFormattingRibbon={pageConflict}', 'suspendFormattingRibbon={false}');
 assert.notEqual(broken,source);
 assert.equal(ribbonContracts(broken),false);
});

test('RC155 regression: widget selection is retained when formatting ribbon closes',()=>{
 assert.match(source,/onClick=\{\(\)=>setRibbonDismissed\(true\)\}/);
 const broken=source.replace('onClick={()=>setRibbonDismissed(true)}','onClick={()=>{setActive(null);setRibbonDismissed(true)}}');
 assert.notEqual(broken,source);
 assert.equal(ribbonContracts(broken),false);
});
