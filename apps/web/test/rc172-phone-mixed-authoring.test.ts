import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {mobilePageWidgets,mobileStageHeight,mergeMobilePositionEdits} from '../src/mobile-page-layout.ts';
import {participantPhoneLayout} from '../src/live-slide-policy.ts';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const widgets=[
 {id:'title',kind:'title',label:'A very long title',position:{x:0,y:4,width:80,height:10}},
 {id:'question',kind:'question',options:[{label:'One'},{label:'Two'}],position:{x:2,y:25,width:90,height:32}},
 {id:'rating',kind:'rating',position:{x:10,y:65,width:50,height:18}},
 {id:'footer',kind:'footer',position:{x:5,y:94,width:90,height:6}},
];
const toPixels=(p:NonNullable<(typeof widgets)[number]['position']>,h:number)=>({top:p.y*h/100,bottom:(p.y+(p.height??0))*h/100});

test('RC172 manual smartphone placement reserves space for automatic interactive widgets',()=>{
 const mobile={positions:{title:{x:3,y:5,width:94,height:43,rotation:0}}};
 const h=mobileStageHeight(widgets,mobile);
 const planned=mobilePageWidgets(widgets,mobile);
 assert.deepEqual(planned.find(w=>w.id==='title')!.position,mobile.positions.title);
 const title=toPixels(planned.find(w=>w.id==='title')!.position!,h);
 for(const w of planned.filter(w=>w.id!=='title')){
  const p=toPixels(w.position!,h);
  assert.ok(p.top>=title.bottom+7,`auto ${w.id} must not cover a manually placed title`);
  assert.ok(p.bottom<=h-14,`auto ${w.id} must stay on the phone page`);
 }
 assert.ok(h>720,'the page grows when the manual slot makes the original stage too short');
 assert.deepEqual(participantPhoneLayout(widgets,mobile),{widgets:planned,height:h},'live and editor geometry must agree');
});

test('RC172 manual bottom content cannot hide the automatic footer',()=>{
 const mobile={positions:{rating:{x:6,y:82,width:88,height:15}}};
 const h=mobileStageHeight(widgets,mobile);
 const planned=mobilePageWidgets(widgets,mobile);
 const f=toPixels(planned.find(w=>w.id==='footer')!.position!,h);
 const r=toPixels(planned.find(w=>w.id==='rating')!.position!,h);
 assert.ok(f.bottom<=r.top-7||f.top>=r.bottom+7,'automatic footer does not overlap manually placed rating');
 assert.ok(f.bottom<=h-14,'footer remains visible on the phone stage');
});

test('RC172 automatic placements are not persisted as manual overrides after a content edit',()=>{
 const mobile={positions:{title:{x:5,y:17,width:90,height:20}}};
 const before=mobilePageWidgets(widgets,mobile);
 const next=mergeMobilePositionEdits(widgets,mobile,before);
 assert.deepEqual(next.positions,mobile.positions);
 const extended=[...widgets,{id:'extra',kind:'question',options:[]}];
 assert.ok(mobilePageWidgets(extended,next).find(w=>w.id==='extra')?.position);
 assert.deepEqual(next.positions?.title,mobile.positions.title);
});

test('RC172 compact automatically only clears positions, not manually customized phone font and color',()=>{
 assert.match(ui,/Ricompatta automaticamente/);
 assert.match(ui,/setMobileLayoutDraft\(old=>\(\{\.\.\.old,positions:undefined\}\)\)/);
 assert.doesNotMatch(ui,/setMobileLayoutDraft\(old=>\(\{\.\.\.old,positions:undefined,styles:undefined\}\)\)/);
 assert.match(ui,/mobileHeight=\{mobileStageHeight\(pageWidgets,mobileLayoutDraft\)\}/);
});

test('RC172 automatic layout remains compact when no manually authored geometry is present',()=>{
 const a=mobilePageWidgets(widgets);
 const b=mobilePageWidgets(widgets,{styles:{title:{fontSize:26}}});
 assert.equal(mobileStageHeight(widgets),720);
 assert.deepEqual(a.map(w=>w.position),b.map(w=>w.position));
 assert.equal(b[0].style?.fontSize,26);
});
