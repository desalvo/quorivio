import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {movePageToSlot} from '../src/page-order.ts';
import {rehearsalPageDirection} from '../src/rehearsal-navigation.ts';
import {mobileWidgetHeight,mobilePageWidgets} from '../src/mobile-page-layout.ts';
import {participantPhoneLayoutEnabled,participantStaticWidescreenPage} from '../src/participant-widescreen-policy.ts';

const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('RC268 drops on before, between, after and empty trailing sidebar without losing page IDs',()=>{
 const pages=['a','b','c','d'];
 assert.deepEqual(movePageToSlot(pages,'c',0),['c','a','b','d']);
 assert.deepEqual(movePageToSlot(pages,'a',3),['b','c','a','d']);
 assert.deepEqual(movePageToSlot(pages,'b',4),['a','c','d','b']);
 assert.deepEqual(movePageToSlot(pages,'c',2),pages,'dropping in its own initial slot is a no-op');
 assert.deepEqual(movePageToSlot(pages,'c',3),pages,'dropping in its own final slot is a no-op');
 assert.deepEqual(pages,['a','b','c','d'],'source order is never mutated');
 assert.throws(()=>movePageToSlot(pages,'x',1));
 assert.throws(()=>movePageToSlot(pages,'a',5));
 assert.throws(()=>movePageToSlot(['a','a'],'a',0));
});

test('RC268 preview arrows do not steal navigation from form fields or modified keyboard shortcuts',()=>{
 assert.equal(rehearsalPageDirection({key:'ArrowRight'}),1);
 assert.equal(rehearsalPageDirection({key:'ArrowLeft'}),-1);
 assert.equal(rehearsalPageDirection({key:'PageDown'}),1);
 assert.equal(rehearsalPageDirection({key:'PageUp'}),-1);
 assert.equal(rehearsalPageDirection({key:'ArrowRight',ctrlKey:true}),0);
 assert.equal(rehearsalPageDirection({key:'ArrowLeft',shiftKey:true}),0);
 assert.equal(rehearsalPageDirection({key:'ArrowRight',target:{closest:()=>({})} as unknown as EventTarget}),0);
 assert.equal(rehearsalPageDirection({key:'ArrowRight',target:{closest:()=>null} as unknown as EventTarget}),1);
});

test('RC268 fullscreen fits desktop canvas to viewport height and width, hides chrome and exposes previous/next buttons',()=>{
 assert.match(main,/immersive\?height\/720:1/);
 assert.match(main,/root\.style\.zoom='100%'/);
 assert.match(main,/return\(\)=>\{root\.style\.zoom=previous\}/);
 assert.match(main,/rehearsalPageDirection\(event\)/);
 assert.match(main,/className="rehearsal-fullscreen-prev"/);
 assert.match(main,/className="rehearsal-fullscreen-next"/);
 assert.match(css,/\.rehearsal-shell\.rehearsal-immersive:fullscreen>\.rehearsal-toolbar,[\s\S]*?rehearsal-footer\{display:none!important\}/);
 assert.match(css,/\.rehearsal-desktop-viewport\.immersive\{[\s\S]*?height:100%!important/);
});

test('RC268 every thumbnail gap is a drop zone and empty rail opens a contextual menu',()=>{
 assert.match(main,/function openSidebarEmptyMenu\(/);
 assert.match(main,/onContextMenu=\{e=>\{if\(\(e\.target as HTMLElement\)\.closest\('\.page-editor-thumb-row/);
 assert.match(main,/onClick=\{e=>\{if\(\(e\.target as HTMLElement\)\.closest\('button,input/);
 assert.match(main,/data-insert-index=\{i\}/);
 assert.match(main,/data-insert-index=\{snap\.activities\.length\}/);
 assert.match(main,/dropPageAtSlot\(id,i\)/);
 assert.match(main,/dropPageAtSlot\(id,snap\.activities\.length\)/);
 assert.match(css,/\.page-editor-drop-slot\[data-active="true"\]/);
});

test('RC268 QR and result auto mobile dimensions and constraints are independent of desktop',()=>{
 assert.ok(mobileWidgetHeight({id:'qr',kind:'qr'})>=210);
 assert.ok(mobileWidgetHeight({id:'result',kind:'results-button'})>=280);
 assert.ok(mobileWidgetHeight({id:'few',kind:'results-button',resultTopCount:1})<mobileWidgetHeight({id:'many',kind:'results-button',resultTopCount:5}));
 assert.ok(mobileWidgetHeight({id:'qr',kind:'qr',showQrUrl:false})<mobileWidgetHeight({id:'qr',kind:'qr',showQrUrl:true}));
 const planned=mobilePageWidgets([{id:'title',kind:'title'},{id:'qr',kind:'qr'},{id:'result',kind:'results-button'}]);
 const qr=planned.find(w=>w.id==='qr')?.position;
 const result=planned.find(w=>w.id==='result')?.position;
 assert.ok(qr&&result&&result.y>=qr.y+qr.height!);
 const manual={positions:{qr:{x:3,y:10,width:55,height:26}}};
 assert.deepEqual(mobilePageWidgets([{id:'qr',kind:'qr'}],manual)[0].position,manual.positions.qr);
 assert.match(css,/\[data-widget-kind="qr"\] \.participant-access-qr>img\{/);
 assert.match(css,/max-width:190px!important;max-height:190px!important/);
 assert.match(css,/\[data-widget-kind="results-button"\] \.linked-result-pair\{/);
 assert.match(css,/flex-wrap:wrap!important;white-space:normal!important/);
});


test('RC268 imported PDFs and pages without resizeable elements stay 16:9 only while shown to phone participants',()=>{
 const imported={type:'slide',page_design:{importedImageFit:'cover',backgroundAssetId:'pdf-asset',widgets:[]}};
 const plain={type:'slide',page_design:{widgets:[],backgroundAssetId:'image-asset'}};
 const inheritedOnly={type:'slide',page_design:{backgroundColor:'#fff'}};
 const interactive={type:'slide',page_design:{widgets:[{kind:'question'}]}};
 const editableImage={type:'slide',page_design:{widgets:[{kind:'image'}]}};
 const poll={type:'poll',page_design:{widgets:[]}};
 assert.equal(participantStaticWidescreenPage(imported),true);
 assert.equal(participantStaticWidescreenPage(plain),true);
 assert.equal(participantStaticWidescreenPage(inheritedOnly),true);
 assert.equal(participantStaticWidescreenPage(interactive),false);
 assert.equal(participantStaticWidescreenPage(editableImage),false);
 assert.equal(participantStaticWidescreenPage(poll),false);
 assert.equal(participantStaticWidescreenPage(null),false);
 // Page transitions recompute from the current page, not the previous page.
 assert.equal(participantPhoneLayoutEnabled(true,false,false,imported),false);
 assert.equal(participantPhoneLayoutEnabled(true,false,false,interactive),true);
 assert.equal(participantPhoneLayoutEnabled(true,false,false,plain),false);
 assert.equal(participantPhoneLayoutEnabled(true,false,false,interactive),true);
 // Desktop, accessible reading and explicit user selection remain independent.
 assert.equal(participantPhoneLayoutEnabled(false,false,false,interactive),false);
 assert.equal(participantPhoneLayoutEnabled(true,true,false,interactive),false);
 assert.equal(participantPhoneLayoutEnabled(true,false,true,imported),true);
 assert.match(main,/participantPhoneLayoutEnabled\(participantPhoneMode,participantReadingMode,participantModeExplicit,entry\?\.activity\)/);
 assert.match(main,/participantStaticWidescreenPage\(audienceActivity\)\?<div className="rehearsal-phone-widescreen-frame"/);
 assert.match(main,/aria-pressed=\{!participantReadingMode&&!audiencePortrait\}/);
 assert.match(css,/\.rehearsal-phone-widescreen-frame/);
});
