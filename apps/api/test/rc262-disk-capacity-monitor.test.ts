import test from 'node:test';
import assert from 'node:assert/strict';
import {diskReading,readDatabaseDisk,readApplicationDisk,nextDiskAlertAction,diskAlertStateKey,DB_DISK_SAMPLE_MAX_AGE_SECONDS} from '../src/disk-monitor.ts';

test('RC262 real filesystem sample: capacity, available and 90% threshold are consistent',()=>{
 assert.deepEqual([diskReading(1000,101,'asset').status,diskReading(1000,100,'asset').status],['ok','warning']);
 assert.deepEqual([diskReading(1000,101,'asset').usedBytes,diskReading(1000,100,'asset').usedPercent],[899,90]);
 assert.deepEqual([diskReading(1000,100,'asset').availableBytes,diskReading(1000,100,'asset').totalBytes],[100,1000]);
 assert.equal(diskReading(100,100,'asset').usedPercent,0);
 assert.equal(diskReading(100,0,'asset').usedPercent,100);
});
test('RC262 invalid/unknown disk values are never treated as healthy or used to alert',()=>{
 for(const [total,free] of [[0,0],[-1,0],[100,-1],[100,101],[NaN,0],[Infinity,0],['NaN','5'],[2**60,0]]){
  assert.equal(diskReading(total,free,'asset').status,'unavailable');
 }
});
test('RC262 PostgreSQL sample must come from real recent filesystem probe',()=>{
 const now=Date.now();
 const valid={total_bytes:'100000',available_bytes:'10000',observed_at:new Date(now-20000).toISOString()};
 assert.equal(readDatabaseDisk(valid,now).usedPercent,90);
 assert.equal(readDatabaseDisk(valid,now).status,'warning');
 assert.equal(readDatabaseDisk(null,now).status,'unavailable');
 assert.equal(readDatabaseDisk({...valid,observed_at:new Date(now-DB_DISK_SAMPLE_MAX_AGE_SECONDS*1000-100).toISOString()},now).reason,'stale_sample');
 assert.equal(readDatabaseDisk({...valid,observed_at:new Date(now+65000).toISOString()},now).status,'unavailable');
 assert.equal(readDatabaseDisk({...valid,total_bytes:100,available_bytes:101},now).status,'unavailable');
});
test('RC262 email alerts send once across checks, rearm below 85 and do not flap',()=>{
 assert.equal(nextDiskAlertAction(90,'normal'),'send');
 assert.equal(nextDiskAlertAction(89.99,'normal'),'hold');
 assert.equal(nextDiskAlertAction(92,'alert'),'hold');
 assert.equal(nextDiskAlertAction(88,'alert'),'hold');
 assert.equal(nextDiskAlertAction(85,'alert'),'rearm');
 assert.equal(nextDiskAlertAction(84,'normal'),'hold');
 assert.equal(nextDiskAlertAction(NaN,'normal'),'hold');
 assert.equal(nextDiskAlertAction(101,'normal'),'hold');
});
test('RC262 local statfs uses real available blocks rather than pg_database_size guess',async()=>{
 const result=await readApplicationDisk('/tmp');
 assert.equal(result.status==='ok'||result.status==='warning',true);
 assert.equal(result.totalBytes!>0,true);
 assert.equal((result.availableBytes??-1)>=0,true);
 assert.equal((result.usedBytes??-1)>=0,true);
 assert.equal((result.availableBytes??0)+(result.usedBytes??0),result.totalBytes);
 const missing=await readApplicationDisk('/missing/quorivio/capacity/test');
 assert.equal(missing.status,'unavailable');
});

test('RC262 per-pod scratch disk alert cannot be reset by a healthy replica',()=>{
 assert.equal(diskAlertStateKey('application','pod-a'),'application');
 assert.equal(diskAlertStateKey('database','pod-a'),'database');
 assert.equal(diskAlertStateKey('conversion','pod-a'),'conversion:pod-a');
 assert.equal(diskAlertStateKey('conversion','pod-b'),'conversion:pod-b');
 assert.notEqual(diskAlertStateKey('conversion','pod-a'),diskAlertStateKey('conversion','pod-b'));
});
