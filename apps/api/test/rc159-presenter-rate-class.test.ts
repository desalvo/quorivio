import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
import {apiRateClass,apiRateBudget} from '../src/api-rate-policy.ts';
const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');

test('authenticated presenter reads have a separate bounded budget',()=>{
 assert.equal(apiRateClass('GET','/sessions/01234567-89ab-cdef-0123-456789abcdef','user1'),'presenter-read');
 assert.equal(apiRateBudget('presenter-read'),360);
 assert.equal(apiRateClass('GET','/sessions/01234567-89ab-cdef-0123-456789abcdef',null),'default');
});
test('authorized page-open changes have an independent finite navigation budget',()=>{
 const path='/sessions/01234567-89ab-cdef-0123-456789abcdef/activities/01234567-89ab-cdef-0123-456789abcdef/open';
 assert.equal(apiRateClass('POST',path,'user1'),'presenter-navigation');
 assert.equal(apiRateBudget('presenter-navigation'),180);
 assert.equal(apiRateClass('POST',path,null),'default');
 assert.equal(apiRateClass('POST',path+'/anything','user1'),'default');
 assert.equal(apiRateClass('POST','/sessions/s1/activities/a1/open','user1'),'default');
});
test('sensitive actions, anonymous reads and responses retain the strict 100/min cap',()=>{
 for(const [method,path,user] of [
  ['POST','/join/code/ratings',null], ['POST','/sessions/x/status','user1'],
  ['POST','/sessions/x/reset-to-ready','user1'],['POST','/auth/login',null],
  ['GET','/join/code',null],['GET','/auth/profile','user1'],
  ['PATCH','/sessions/x/activities/a','user1'],
 ] as const){
  assert.equal(apiRateClass(method,path,user),'default',method+' '+path);
 }
 assert.equal(apiRateBudget('default'),100);
});
test('all paths still use one PostgreSQL-backed cross-replica fail-closed quota',()=>{
 assert.match(server,/apiRateClass\(req\.method,req\.path,uid\)/);
 assert.match(server,/apiRateBudget\(rateClass\)/);
 assert.match(server,/ON CONFLICT\(client_hash,bucket\) DO UPDATE SET hits=api_rate_windows\.hits\+1/);
 assert.match(server,/Number\(r\.rows\[0\]\.hits\)>limit/);
 assert.match(server,/rate_limiter_unavailable/);
 assert.match(server,/rateClass==='default'\?'ip:'/);
 assert.match(server,/const uid=auth\(req\)/);
});
