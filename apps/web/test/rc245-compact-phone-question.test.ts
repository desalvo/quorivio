import test from 'node:test';
import assert from 'node:assert/strict';
import {mobileWidgetHeight,mobilePageWidgets,mobileStageHeight} from '../src/mobile-page-layout.ts';

test('RC245 two short answers use a compact 238px question without shrinking touch rows',()=>{
 const question={id:'q',kind:'question',options:[{label:'Yes'},{label:'No'}]};
 assert.equal(mobileWidgetHeight(question),150+44*2);
 const stage=[{id:'title',kind:'title'},question,{id:'footer',kind:'footer'}];
 const rendered=mobilePageWidgets(stage);
 const height=mobileStageHeight(stage);
 const planned=rendered.find(w=>w.id==='q')?.position;
 assert.ok(planned?.height!==undefined);
 assert.ok(Math.abs(planned.height! * height/100 - 238)<0.02);
 assert.equal(height,720,'short three-widget phone page should not require needless scrolling');
});

test('RC245 long answer grows the question and stage; authored phone overrides remain stable',()=>{
 const question={id:'q',kind:'question',options:[{label:'long '.repeat(40)},{label:'No'}]};
 assert.ok(mobileWidgetHeight(question)>238);
 const stage=[{id:'title',kind:'title'},question,{id:'footer',kind:'footer'}];
 const short=[{id:'title',kind:'title'},{id:'q',kind:'question',options:[{label:'Yes'},{label:'No'}]},{id:'footer',kind:'footer'}];
 assert.ok(mobileWidgetHeight(question)>mobileWidgetHeight(short[1]));
 const custom={positions:{q:{x:4,y:15,width:92,height:40,rotation:0}}};
 assert.deepEqual(mobilePageWidgets(stage,custom).find(w=>w.id==='q')?.position,custom.positions.q);
});
