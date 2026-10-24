import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {normalizeJoinCode,canSubmitParticipantAnswer,publicActivityFromSnapshot,nextLiveRetryMs} from '../../web/src/participant-state.ts';
const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
const ui=readFileSync(new URL('../../web/src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../../web/src/style.css',import.meta.url),'utf8');
test('join secret and short join code survive URL normalization',()=>{
 assert.equal(normalizeJoinCode(' ABC123 '),'ABC123');
 assert.equal(normalizeJoinCode('a0b1c2d3e4'),'A0B1C2D3E4');
 assert.equal(normalizeJoinCode('https://example.org/join/abC_123-X'),'abC_123-X');
 assert.equal(normalizeJoinCode('/join/ABC123'),'ABC123');
 assert.equal(normalizeJoinCode('ABC%31%32%33'),'ABC123');
});
test('invalid or malicious URL segments cannot break join route',()=>{
 assert.equal(normalizeJoinCode('%FF'),'');
 assert.equal(normalizeJoinCode('a/b/c'),'');
 assert.equal(normalizeJoinCode('..'), '');
 assert.equal(normalizeJoinCode('x'.repeat(200)).length,128);
});
test('required answer readiness respects each mode',()=>{
 const blank={answer:'',multipleAnswers:[],freeText:'  '};
 for(const mode of ['single','multiple','text','file'])assert.equal(canSubmitParticipantAnswer(mode,true,blank),false);
 assert.equal(canSubmitParticipantAnswer('single',true,{...blank,answer:'yes'}),true);
 assert.equal(canSubmitParticipantAnswer('multiple',true,{...blank,multipleAnswers:['yes']}),true);
 assert.equal(canSubmitParticipantAnswer('text',true,{...blank,freeText:' answer '}),true);
 assert.equal(canSubmitParticipantAnswer('file',true,{...blank,answer:'asset-id'}),true);
 for(const mode of ['single','multiple','text','file'])assert.equal(canSubmitParticipantAnswer(mode,false,blank),true);
});
test('participant snapshot only renders the currently open activity of active session',()=>{
 const base={session:{status:'active',current_activity_id:'a'},activities:[{id:'a',status:'open',title:'Yes'},{id:'b',status:'open'}]};
 assert.equal(publicActivityFromSnapshot(base).title,'Yes');
 assert.equal(publicActivityFromSnapshot({...base,session:{...base.session,status:'paused'}}),null);
 assert.equal(publicActivityFromSnapshot({...base,session:{...base.session,status:'closed'}}),null);
 assert.equal(publicActivityFromSnapshot({...base,activities:[{id:'a',status:'closed'}]}),null);
 assert.equal(publicActivityFromSnapshot({...base,session:{...base.session,current_activity_id:null}}),null);
 assert.equal(publicActivityFromSnapshot({...base,activities:null}),null);
});
test('WebSocket reconnect backoff is bounded and deterministic',()=>{
 assert.deepEqual([0,1,2,3,4,5,6,100].map(nextLiveRetryMs),[1800,3600,7200,14400,28800,30000,30000,30000]);
});
test('participation recovery API never exposes identity or cookie',()=>{
 const route=server.split("app.get('/api/join/:code/participation'")[1]?.split("app.post('/api/join/:code'")[0]||'';
 assert.ok(route.includes("Cache-Control','no-store, private'"));
 assert.match(route,/token_hash=\$2/);
 assert.match(route,/res\.json\(\{joined:false\}\)/);
 assert.match(route,/res\.json\(\{joined:\(found\.rowCount\?\?0\)>0\}\)/);
 assert.doesNotMatch(route,/res\.json\(\{.*pseudonym/);
});
test('browser recovers participation without storing participant token in JS',()=>{
 assert.match(ui,/\/participation`\)/);
 assert.match(ui,/setJoined\(v\.joined===true\)/);
 assert.doesNotMatch(ui,/localStorage\.setItem\('quorivio_participant_token'/);
});
test('participant submission disables duplicate clicks and announces success',()=>{
 assert.match(ui,/if\(votePending\|\|sent\|\|!entry\?\.activity\|\|!joined\)return/);
 assert.match(ui,/disabled=\{votePending\|\|!canSubmitParticipantAnswer/);
 assert.match(ui,/sent\?<div className="success" role="status" aria-live="polite"/);
});
test('responsive participant widgets do not overlap on phone viewport',()=>{
 assert.match(css,/\.audience-widget-layout>\.page-widget\[style\*="absolute"\]\{position:relative!important/);
 assert.match(css,/min-height:44px/);
});
test('skip link and keyboard pressed state are exposed',()=>{
 assert.match(ui,/className="skip-link" href="#main-content"/);
 assert.match(ui,/aria-pressed=\{entry\.activity\.answer_mode/);
 assert.match(ui,/role="group" aria-label="Opzioni di risposta"/);
});
