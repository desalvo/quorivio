import test from 'node:test';
import assert from 'node:assert/strict';
import {participantPhoneLayout} from '../src/live-slide-policy.ts';

const fixture = [
  {id:'title',kind:'title'},
  {id:'question',kind:'question',options:[{label:'Yes'},{label:'No'}]},
  {id:'rating',kind:'rating'},
  {id:'topic',kind:'topic-question'},
  {id:'line',kind:'line'},
  {id:'shape',kind:'shape'},
  {id:'secret-results',kind:'results-button'},
  {id:'secret-count',kind:'participant-count'},
  {id:'footer',kind:'footer'},
];

test('RC217 RC207 44px choices grow the public stage without phantom presenter height',()=>{
 const publicStage=participantPhoneLayout(fixture);
 assert.equal(publicStage.height,1028,'two public answers require 44px rows, not RC176 29px rows');
 assert.deepEqual(publicStage.widgets.map(w=>w.kind),
  ['title','question','rating','topic-question','line','shape','footer']);
 const allKinds=fixture.filter(w=>w.kind!=='results-button'&&w.kind!=='participant-count');
 assert.equal(publicStage.widgets.length,allKinds.length);
 assert.equal(publicStage.widgets.at(-1)?.position?.y!==undefined,true);
 assert.ok((publicStage.widgets.at(-1)?.position?.y??0)>90,'public footer stays near the end');
});

test('RC217 stage grows with long options but does not reserve presenter-only widgets',()=>{
 const long=fixture.map(w=>w.kind==='question'?{...w,options:[{label:'A'.repeat(255)},{label:'No'}]}:w);
 const publicStage=participantPhoneLayout(long);
 assert.ok(publicStage.height>1028+100);
 assert.equal(participantPhoneLayout([...long,
  {id:'other-private',kind:'results-button'},{id:'other-count',kind:'participant-count'}]).height,
  publicStage.height,'more presenter-only tools may not add invisible height');
 assert.ok(publicStage.widgets.every(w=>w.kind!=='results-button'&&w.kind!=='participant-count'));
});
