import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validPageDesign} from '../src/domain.ts';
import {responseParticipationPercent,responseParticipationGaugeSize} from '../../web/src/response-participation.ts';

const widget={id:'results',kind:'results-button'};
test('RC333 gauge is disabled by default; optional only for result widget; scale 20..100',()=>{
 assert.equal(validPageDesign({widgets:[widget]}),true);
 assert.equal(validPageDesign({widgets:[{...widget,showResponseParticipation:true,responseParticipationGaugeSize:20}]}),true);
 assert.equal(validPageDesign({widgets:[{...widget,responseParticipationGaugeSize:100}]}),true);
 for(const invalid of [19,101,50.5,-1,'60'])assert.equal(validPageDesign({widgets:[{...widget,responseParticipationGaugeSize:invalid}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'question',kind:'question',showResponseParticipation:true}]}),false);
 assert.equal(validPageDesign({widgets:[{...widget,showResponseParticipation:'yes'}]}),false);
 assert.equal(responseParticipationGaugeSize(undefined),60);
 assert.equal(responseParticipationGaugeSize(5),20);
 assert.equal(responseParticipationGaugeSize(200),100);
});
test('RC333 only one response per connected user, bounded 0..100',()=>{
 assert.equal(responseParticipationPercent(0,0),0);
 assert.equal(responseParticipationPercent(0,500),0);
 assert.equal(responseParticipationPercent(1,500),0);
 assert.equal(responseParticipationPercent(250,500),50);
 assert.equal(responseParticipationPercent(500,500),100);
 assert.equal(responseParticipationPercent(650,500),100);
 assert.equal(responseParticipationPercent(-2,500),0);
 assert.equal(responseParticipationPercent(40,-1),0);
 assert.equal(responseParticipationPercent(Number.NaN,500),0);
 assert.equal(responseParticipationPercent(Number.POSITIVE_INFINITY,500),0);
});
test('RC333 live owner-only response count never leaks participant identities',()=>{
 const api=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
 const ui=readFileSync(new URL('../../web/src/main.tsx',import.meta.url),'utf8');
 assert.match(api,/count\(DISTINCT live\.participant_id\)::int AS answered/);
 assert.match(api,/INNER JOIN responders r/);
 assert.match(api,/live\.last_seen>now\(\)-interval '50 seconds'/);
 assert.match(api,/responded_connected_participants:await respondedConnectedParticipants\(sid\)/);
 const p=api.slice(api.indexOf('function participantSnapshot('),api.indexOf('const webRoot=',api.indexOf('function participantSnapshot(')));
 assert.doesNotMatch(p,/responded_connected_participants/);
 assert.match(ui,/checked=\{w.showResponseParticipation===true\}/);
 assert.match(ui,/participation=\{\{responded:snapshot\.responded_connected_participants\?\?0,connected:snapshot\.connected_participants\?\?0\}\}/);
});
