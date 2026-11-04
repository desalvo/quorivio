import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {participantVisibleWidgets, participantPhoneLayout, widgetTitleVisible} from '../src/live-slide-policy.ts';
import {resolveSlideMasterWidgets} from '../src/master-widget-utils.ts';
import {mobilePageWidgets} from '../src/mobile-page-layout.ts';

const ui=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
test('RC167 public projection uses the same actual widgets as participant rehearsal, without ghost presenter tools',()=>{
 const widgets=[{id:'title',kind:'title'}, {id:'line',kind:'line',label:'Legacy line caption',showTitle:true},
  {id:'shape',kind:'shape',label:'Legacy shape caption',showTitle:true},
  {id:'q',kind:'question'}, {id:'stats',kind:'results-button',targetWidgetId:'q'},
  {id:'count',kind:'participant-count'}, {id:'footer',kind:'footer'}];
 const master=[{id:'master-count',kind:'participant-count'}, {id:'master-shape',kind:'shape'}];
 const resolved=resolveSlideMasterWidgets(widgets,master);
 const audience=participantVisibleWidgets(resolved);
 assert.deepEqual(audience.map(w=>w.kind),['shape','title','line','shape','question','footer']);
 assert.deepEqual(participantPhoneLayout(resolved).widgets.map(w=>w.id),audience.map(w=>w.id));
 assert.deepEqual(resolved.map(w=>w.id).filter(x=>x==='stats'||x==='count'),['stats','count']);
});
test('RC167 lines/forms never expose captions, QR caption is opt-in, content titles preserve author intent',()=>{
 for(const kind of ['line','shape'])for(const showTitle of [undefined,false,true])
  assert.equal(widgetTitleVisible({kind,showTitle}),false,kind+' '+showTitle);
 assert.equal(widgetTitleVisible({kind:'qr'}),false);
 assert.equal(widgetTitleVisible({kind:'qr',showTitle:true}),true);
 assert.equal(widgetTitleVisible({kind:'qr',showTitle:false}),false);
 assert.equal(widgetTitleVisible({kind:'question'}),true);
 assert.equal(widgetTitleVisible({kind:'title',showTitle:false}),false);
});
test('RC167 all three stage roots apply the shared visibility policy and public graphics have no caption JSX',()=>{
 assert.match(ui,/import \{participantVisibleWidgets,participantPhoneLayout,widgetTitleVisible\} from '\.\/live-slide-policy'/);
 assert.equal((ui.match(/data-show-title=\{widgetTitleVisible\(w\)\}/g)||[]).length,4);
 assert.match(ui,/viewer==='presenter'\?.*?:\(mobile\?participantPhoneLayout\(widgets/);
 assert.match(ui,/audiencePortrait\?audiencePhoneLayout\.widgets:participantReadingMode\?audienceReadingWidgets:audienceVisibleWidgets/);
 assert.match(ui,/\(w\.kind==='shape'\|\|w\.kind==='line'\)\?null:/);
 assert.doesNotMatch(ui,/\(w\.kind==='shape'\|\|w\.kind==='line'\)\?\(w\.showTitle===false\?null:/);
});
