import test from 'node:test';
import assert from 'node:assert/strict';
import {canSubmitRehearsalAnswer,commitRehearsalAnswer,REHEARSAL_REACTION_PREFIX} from '../src/rehearsal-responses.ts';
import {sampleStatisticRows} from '../src/widget-results.ts';
const question={id:'q-1',kind:'question',options:[{id:'a',label:'Sì'},{id:'b',label:'No'}]};
test('draft option selection alone never changes the presenter sample statistics',()=>{
 const seed=813, baseline=sampleStatisticRows(question,seed,{});
 const draft={['q-1']:'a'};
 const notSent=sampleStatisticRows(question,seed,{});
 assert.deepEqual(notSent,baseline);
 const sent=commitRehearsalAnswer({},'q-1',draft['q-1'],'single');
 const after=sampleStatisticRows(question,seed,sent);
 assert.equal(after.find(r=>r.id==='a')!.count,baseline.find(r=>r.id==='a')!.count+1);
 assert.equal(after.find(r=>r.id==='b')!.count,baseline.find(r=>r.id==='b')!.count);
});
test('one-shot per independent question and document, even on double submit',()=>{
 const first=commitRehearsalAnswer({},'widget:sub-a','yes','single');
 assert.equal(commitRehearsalAnswer(first,'widget:sub-a','no','single'),first);
 const next=commitRehearsalAnswer(first,'widget:sub-b',['x','y'],'multiple');
 assert.deepEqual(next,{'widget:sub-a':'yes','widget:sub-b':['x','y']});
 // Mutating draft cannot mutate a submitted multiple-choice selection.
 const draft=['x','y'];const submitted=commitRehearsalAnswer({},'w',draft,'multiple');draft.push('z');assert.deepEqual(submitted.w,['x','y']);
});
test('rejects blank, empty and oversized drafts, including filenames',()=>{
 for(const value of [undefined,'',[]] as const){
  assert.equal(canSubmitRehearsalAnswer('single',value),false);
  assert.equal(canSubmitRehearsalAnswer('multiple',value),false);
 }
 assert.equal(canSubmitRehearsalAnswer('text','\t\n'),false);
 assert.equal(canSubmitRehearsalAnswer('text','a'.repeat(5001)),false);
 assert.equal(canSubmitRehearsalAnswer('text','à prova'),true);
 assert.equal(canSubmitRehearsalAnswer('file','example.pdf'),true);
 assert.equal(canSubmitRehearsalAnswer('file','a'.repeat(256)),false);
 assert.equal(canSubmitRehearsalAnswer('unknown','yes'),false);
 const empty={x:'yes'};
 assert.equal(commitRehearsalAnswer(empty,'y','  ','text'),empty);
});
test('one reaction for the whole page, not one per reaction widget',()=>{
 const page=REHEARSAL_REACTION_PREFIX+'activity1';
 const sent=commitRehearsalAnswer({},page,'👍','reaction');
 assert.equal(commitRehearsalAnswer(sent,page,'❤️','reaction'),sent);
 assert.equal(commitRehearsalAnswer(sent,REHEARSAL_REACTION_PREFIX+'activity2','❤️','reaction')[REHEARSAL_REACTION_PREFIX+'activity2'],'❤️');
});
test('reset is memory-only and produces no persistence calls',()=>{
 const sent=commitRehearsalAnswer({},'q-1','a','single');
 assert.equal(sent['q-1'],'a');assert.equal(Object.keys({}).length,0);
 assert.equal(canSubmitRehearsalAnswer('rating','0'),true);
 assert.equal(canSubmitRehearsalAnswer('rating','10'),true);
});
