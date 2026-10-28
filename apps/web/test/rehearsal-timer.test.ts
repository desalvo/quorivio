import test from 'node:test';
import assert from 'node:assert/strict';
import {rehearsalDurationSeconds,rehearsalExpired,maySubmitTimedRehearsal} from '../src/rehearsal-timer.ts';

test('preview clock prefers valid widget duration, then page duration, then safe default',()=>{
 assert.equal(rehearsalDurationSeconds(45,10),45);
 assert.equal(rehearsalDurationSeconds(0,70),70);
 assert.equal(rehearsalDurationSeconds(NaN,Infinity),30);
 assert.equal(rehearsalDurationSeconds(-1,0),30);
 assert.equal(rehearsalDurationSeconds('15',30),30);
 assert.equal(rehearsalDurationSeconds(3601,120),120);
});
test('deadline is exact and rejects late one-shot submissions',()=>{
 const start=1_000_000;
 assert.equal(rehearsalExpired(start,30,start+29_999),false);
 assert.equal(rehearsalExpired(start,30,start+30_000),true);
 assert.equal(maySubmitTimedRehearsal(start,30,start+29_999,false),true);
 assert.equal(maySubmitTimedRehearsal(start,30,start+30_000,false),false);
 assert.equal(maySubmitTimedRehearsal(start,30,start+100,true),false);
 assert.equal(rehearsalExpired(start,30,start),false);
});
test('pane switches keep one deadline; page entry and restart create a new independent clock',()=>{
 const first=2_000_000,second=first+32_000;
 assert.equal(maySubmitTimedRehearsal(first,30,second,false),false);
 assert.equal(maySubmitTimedRehearsal(second,30,second,false),true);
});
