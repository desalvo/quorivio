import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {participantPhoneLayout,participantVisibleWidgets} from '../src/live-slide-policy.ts';
import {mobilePageWidgets,mobileStageHeight} from '../src/mobile-page-layout.ts';
import {resolveSlideMasterWidgets} from '../src/master-widget-utils.ts';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const p=(x:number,y:number,width=70,height=15)=>({x,y,width,height,rotation:0});
const visible=[
 {id:'title',kind:'title',position:p(5,5)},
 {id:'question',kind:'question',options:[{id:'yes',label:'Yes'},{id:'no',label:'No'}],position:p(10,25)},
 {id:'rating',kind:'rating',position:p(10,55)},
 {id:'footer',kind:'footer',position:p(5,92,90,6)},
];
const privateTools=[
 {id:'results',kind:'results-button',position:p(55,35)},
 {id:'count',kind:'participant-count',position:p(55,45)},
];

test('RC168 invisible presenter-only widgets do not reserve smartphone height or stacking slots',()=>{
 const reference=participantPhoneLayout(visible);
 const withPrivate=participantPhoneLayout([visible[0],privateTools[0],visible[1],privateTools[1],visible[2],visible[3]]);
 assert.deepEqual(withPrivate,reference);
 assert.deepEqual(withPrivate.widgets.map(w=>w.id),['title','question','rating','footer']);
 assert.equal(withPrivate.height,mobileStageHeight(visible));
 assert.ok(mobileStageHeight([...visible,...privateTools])>withPrivate.height);
 assert.notDeepEqual(mobilePageWidgets([...visible,...privateTools]).filter(w=>!privateTools.some(x=>x.id===w.id)),reference.widgets);
 const footer=withPrivate.widgets.at(-1)!;
 assert.ok(footer.position!.y+footer.position!.height!<=100);
 assert.ok(footer.position!.y+footer.position!.height!>95);
});

test('RC168 master controls are filtered before mobile sizing, not only before DOM rendering',()=>{
 const master=[{id:'master-count',kind:'participant-count',position:p(80,40)}, {id:'master-footer',kind:'footer',position:p(4,92,92,6)}];
 const page=[{id:'title',kind:'title',position:p(5,5)}, {id:'question',kind:'question',position:p(8,35)}];
 const resolved=resolveSlideMasterWidgets(page,master);
 const phone=participantPhoneLayout(resolved);
 const audience=participantVisibleWidgets(resolved);
 assert.deepEqual(phone.widgets.map(w=>w.id),mobilePageWidgets(audience).map(w=>w.id));
 assert.equal(phone.height,mobileStageHeight(audience));
 assert.ok(phone.widgets.some(w=>w.id==='inherited-master-footer'));
 assert.ok(!phone.widgets.some(w=>w.id==='inherited-master-count'));
});

test('RC168 custom phone geometry and typography survive presenter-only filtering',()=>{
 const edited={positions:{question:p(3,18,94,37)},styles:{question:{fontSize:28,fontFamily:'Georgia'}}};
 const baseline=participantPhoneLayout(visible,edited);
 const withPrivate=participantPhoneLayout([...visible,...privateTools],edited);
 assert.deepEqual(withPrivate,baseline);
 assert.deepEqual(withPrivate.widgets.find(w=>w.id==='question')?.position,edited.positions.question);
 assert.equal(withPrivate.widgets.find(w=>w.id==='question')?.style?.fontFamily,'Georgia');
 assert.deepEqual(visible.map(w=>w.position),[p(5,5),p(10,25),p(10,55),p(5,92,90,6)]);
});

test('RC168 both public and rehearsal stages consume the same filtered phone layout',()=>{
 assert.match(ui,/const audiencePhoneLayout=participantPhoneLayout\(audienceAuthoredWidgets/);
 assert.match(ui,/height:audiencePhoneLayout\.height/);
 assert.match(ui,/audiencePortrait\?audiencePhoneLayout\.widgets:participantReadingMode\?audienceReadingWidgets:audienceVisibleWidgets/);
 assert.match(ui,/mobile\?participantPhoneLayout\(viewWidgets,viewActivity\?\.page_design\?\.mobile\)\.widgets:participantVisibleWidgets\(viewWidgets\)/);
 assert.match(ui,/PhoneRehearsalStage height=\{participantPhoneLayout\(widgets,audienceActivity\?\.page_design\?\.mobile\)\.height\}/);
 assert.doesNotMatch(ui,/participantVisibleWidgets\(mobilePageWidgets\(/);
});
