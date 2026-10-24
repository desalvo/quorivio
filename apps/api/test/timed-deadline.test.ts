import test from 'node:test';
import assert from 'node:assert/strict';
import {timedDeadline} from '../src/timed-deadline.ts';
const start='2026-10-24T10:00:00.000Z';
test('deadline includes exact boundary and excludes next millisecond',()=>{
 assert.equal(timedDeadline(start,30,'2026-10-24T10:00:30.000Z').valid,true);
 assert.equal(timedDeadline(start,30,'2026-10-24T10:00:30.001Z').valid,false);
});
test('elapsed time uses database time independently of API host clocks',()=>{
 assert.deepEqual(timedDeadline(start,30,'2026-10-24T10:00:00.123Z'),{valid:true,elapsedMs:123});
});
test('rejects missing or future opening time and invalid duration',()=>{
 assert.equal(timedDeadline(null,30,start).valid,false);
 assert.equal(timedDeadline('2026-10-24T10:00:10Z',30,start).valid,false);
 assert.equal(timedDeadline(start,0,start).valid,false);
 assert.equal(timedDeadline(start,601,start).valid,false);
});
