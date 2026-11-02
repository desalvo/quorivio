import {test} from 'node:test';
import assert from 'node:assert/strict';
import {classifyBackgroundUploadFailure,backgroundUploadLog} from '../src/background-upload-failure.ts';

const failure=(code:string)=>Object.assign(Error('private path /app/assets/private/abc'),{code});
test('Kubernetes PVC permissions and capacity are distinguishable without leaking paths',()=>{
 for(const code of ['EACCES','EPERM','EROFS']){
  assert.deepEqual(classifyBackgroundUploadFailure('receiving',failure(code)),{status:507,code:'background_storage_unavailable',category:'volume_permissions'});
 }
 for(const code of ['ENOSPC','EDQUOT']){
  assert.equal(classifyBackgroundUploadFailure('applying',failure(code)).category,'volume_capacity');
 }
 assert.equal(classifyBackgroundUploadFailure('applying',failure('ESTALE')).status,503);
});
test('scanner failures remain fail closed, even when clamd TCP is reachable',()=>{
 for(const value of ['antivirus_timeout','antivirus_connection_error','antivirus_scan_failed','antivirus_premature_response']){
  const result=classifyBackgroundUploadFailure('scanning',Error(value));
  assert.equal(result.status,503);
  assert.equal(result.code,'antivirus_unavailable');
 }
 assert.deepEqual(classifyBackgroundUploadFailure('scanning',Error('malware_detected')),{status:422,code:'malware_detected',category:'infected_file'});
});
test('bad images are 415 while database failures expose no SQL',()=>{
 assert.equal(classifyBackgroundUploadFailure('receiving',Error('invalid_media_signature')).status,415);
 assert.equal(classifyBackgroundUploadFailure('receiving',Error('upload_length_mismatch')).status,400);
 assert.equal(classifyBackgroundUploadFailure('receiving',Error('upload_too_large')).status,413);
 assert.deepEqual(classifyBackgroundUploadFailure('applying',failure('23505')),{status:503,code:'background_database_unavailable',category:'database_error'});
 assert.equal(classifyBackgroundUploadFailure('registering',Error('private pg response')).code,'background_database_unavailable');
});
test('logs contain phase and category, no owner ID, path or raw server errors',()=>{
 for(const phase of ['authorization','receiving','scanning','registering','applying'] as const){
  const log=backgroundUploadLog(phase,failure('EACCES'));
  assert.match(log,/"phase"/);
  assert.match(log,/"category"/);
  assert.doesNotMatch(log,/private|\/app\/|abc/);
 }
});
