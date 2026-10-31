import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {livePageTimerSeconds,livePageTimerExpired} from '../src/page-timer.ts';
import {validPageDesign} from '../src/domain.ts';
const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
test('server-side countdown uses earliest valid page timer and PostgreSQL time',()=>{
 const design={widgets:[{id:'a',kind:'timer',durationSeconds:25},{id:'b',kind:'timer',durationSeconds:10}]};
 assert.equal(livePageTimerSeconds(design),10);
 const opened='2026-01-01T10:00:00.000Z';
 assert.equal(livePageTimerExpired(design,opened,'2026-01-01T10:00:09.999Z'),false);
 assert.equal(livePageTimerExpired(design,opened,'2026-01-01T10:00:10.000Z'),true);
 assert.equal(livePageTimerExpired(design,null,'2026-01-01T10:00:00.000Z'),true);
 assert.equal(livePageTimerExpired({widgets:[{kind:'question'}]},null,'2026-01-01T10:00:00.000Z'),false);
});
test('server rejects malformed durations and accepts 60 minute timer',()=>{
 assert.equal(validPageDesign({widgets:[{id:'t',kind:'timer',durationSeconds:3600}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'t',kind:'timer',durationSeconds:3601}]}),false);
});
test('live write guard rejects timeouts independently of client state',()=>{
 assert.match(server,/app\.use\('\/api\/join\/:code',async\(req,res,next\)/);
 assert.match(server,/clock_timestamp\(\) AS current_db_time/);
 assert.match(server,/livePageTimerExpired\(data\.rows\[0\]\.page_design/);
 assert.match(server,/status\(409\)\.json\(\{error:'timer_elapsed'\}\)/);
});
