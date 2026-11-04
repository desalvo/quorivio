import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {mobilePageWidgets,mergeMobilePositionEdits,pruneMobilePageLayout} from '../src/mobile-page-layout.ts';
import {validPageDesign} from '../../api/src/domain.ts';

const ui=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const widgets=[{id:'qr',kind:'qr',label:'Accesso',position:{x:10,y:14,width:25,height:20}},{id:'title',kind:'title',label:'Benvenuti',position:{x:2,y:2,width:85,height:9}}];
test('RC162 smartphone toggle is a real keyboard-accessible switch above the editable canvas',()=>{
 assert.match(ui,/className="editor-device-switch"[\s\S]*?type="checkbox" role="switch" aria-label="Modifica layout Smartphone"/);
 assert.match(ui,/onChange=\{e=>setCanvasDevice\(e\.target\.checked\?'phone':'desktop'\)\}/);
 assert.ok(ui.indexOf('className="editor-device-switch"')<ui.indexOf('className="editor-canvas-slot"'));
 assert.match(ui,/data-editor-device=\{canvasDevice\}/);
 assert.match(ui,/widgets=\{canvasDevice==='phone'\?mobilePageWidgets\(pageWidgets,mobileLayoutDraft\):pageWidgets\}/);
 assert.match(css,/\.editor-device-slider input:checked\+\.editor-device-slider-track/);
});
test('RC162 smartphone remains automatic until the presenter actually changes a position',()=>{
 const automatic=mobilePageWidgets(widgets);
 const untouched=mergeMobilePositionEdits(widgets,{},automatic);
 assert.equal(untouched.positions,undefined,'unmodified auto layout is not frozen');
 const changed=automatic.map((w,i)=>i===0?{...w,position:{...w.position!,x:12,width:80}}:w);
 const custom=mergeMobilePositionEdits(widgets,{},changed);
 assert.deepEqual(custom.positions?.qr,changed[0].position);
 assert.equal(custom.positions?.title,undefined);
 assert.deepEqual(mobilePageWidgets(widgets,custom)[0].position,changed[0].position);
 const updatedDesktop=[widgets[0],{...widgets[1],label:'Titolo aggiornato'}];
 assert.equal(mobilePageWidgets(updatedDesktop,custom)[1].label,'Titolo aggiornato');
 assert.deepEqual(updatedDesktop[0].position,widgets[0].position,'desktop geometry unchanged');
 const afterStyle=mergeMobilePositionEdits(widgets,custom,mobilePageWidgets(widgets,custom).map(w=>({...w,label:'Changed'})));
 assert.deepEqual(afterStyle.positions,custom.positions,'style-only changes must not freeze auto positions');
 const removed=mergeMobilePositionEdits(widgets,custom,changed.filter(w=>w.id!=='qr'));
 assert.equal(removed.positions?.qr,undefined,'deleted widgets do not leave obsolete overrides');
});
test('RC162 QR title defaults hidden, URL is optional, and validation rejects wrong types/other widgets',()=>{
 assert.equal(validPageDesign({widgets:[{id:'q',kind:'qr',showTitle:false,showQrUrl:true}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'q',kind:'qr',showQrUrl:false}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'q',kind:'qr'}]}),true,'legacy QR widgets remain compatible');
 assert.equal(validPageDesign({widgets:[{id:'q',kind:'qr',showQrUrl:'false'}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'s',kind:'shape',showQrUrl:false}]}),false);
 assert.match(ui,/widget\.showTitle===true&&<strong><WidgetStyledText text=\{widget\.label\|\|'Accesso partecipanti'\}/);
 assert.match(ui,/widget\.showQrUrl!==false&&<span className="participant-qr-url"/);
 assert.match(ui,/checked=\{w\.showQrUrl!==false\}/);
 assert.match(ui,/kind:k,\.\.\.\(k==='qr'\?\{showTitle:false,showQrUrl:true\}/);
});
test('RC162 QR uses responsive reserved text row instead of hiding URL on resize',()=>{
 assert.match(css,/\.participant-access-qr\{display:grid;grid-template-rows:minmax\(0,1fr\) minmax\(1\.3em,auto\)/);
 assert.match(css,/\.participant-access-qr\[data-qr-show-url="false"\]/);
 assert.match(css,/\.participant-access-qr \.participant-qr-url\{[^}]*min-height:1\.3em/);
 assert.match(css,/\.participant-access-qr>img\{[^}]*max-height:100%/);
});

test('RC162 phone typography overrides inherit other desktop styles and fail closed on invalid values',()=>{
 const withStyle=[{...widgets[0],style:{fontFamily:'Arial',fontSize:20,color:'#123456'}}];
 const mobile={styles:{qr:{fontSize:28}}};
 const view=mobilePageWidgets(withStyle,mobile);
 assert.equal(view[0].style?.fontFamily,'Arial');
 assert.equal(view[0].style?.fontSize,28);
 assert.equal(view[0].style?.color,'#123456');
 assert.equal(withStyle[0].style.fontSize,20,'desktop style stays unchanged');
 assert.equal(validPageDesign({widgets:withStyle,mobile}),true);
 assert.equal(validPageDesign({widgets:withStyle,mobile:{styles:{qr:{fontSize:2}}}}),false);
 assert.equal(validPageDesign({widgets:withStyle,mobile:{styles:{ghost:{fontSize:20}}}}),false);
 assert.equal(validPageDesign({widgets:withStyle,mobile:{styles:{qr:{fontFamily:'Comic Sans MS'}}}}),false);
 const changed=mergeMobilePositionEdits(withStyle,mobile,mobilePageWidgets(withStyle,mobile).map(w=>({...w,style:{...w.style,fontSize:30}})));
 assert.deepEqual(changed.styles?.qr,{fontSize:30});
 const cleaned=pruneMobilePageLayout({styles:{ghost:{fontSize:22}},positions:{ghost:{x:0,y:0,width:50}}},withStyle);
 assert.equal(cleaned.styles,undefined);
 assert.equal(cleaned.positions,undefined);
});

test('RC162 automatic phone layout follows the desktop visual order, not insertion order',()=>{
 const reordered=[{id:'lower',kind:'text',position:{x:3,y:70,width:60,height:15}},
  {id:'higher',kind:'text',position:{x:3,y:15,width:60,height:15}}];
 const mobile=mobilePageWidgets(reordered);
 assert.ok((mobile[1].position?.y||0)<(mobile[0].position?.y||0));
 assert.equal(mobile[0].id,'lower'); // persistent widget identities/order are unchanged
});
