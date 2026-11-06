import test from 'node:test';
import assert from 'node:assert/strict';
import {converterAdmission,converterDeploymentConfigured,validConverterToggle} from '../src/converter-admission.ts';
const env={QUORIVIO_ENABLE_CONVERTER:'true',QUORIVIO_CONVERTER_WORKER_URL:'http://converter:8099',QUORIVIO_WORKER_TOKEN:'a'.repeat(64)};
test('conversion availability is fail closed on deployment prerequisites',()=>{
 assert.deepEqual(converterAdmission(env,null),{deployment_enabled:true,worker_configured:true,admin_enabled:true,enabled:true,blocker:null});
 assert.equal(converterAdmission({...env,QUORIVIO_ENABLE_CONVERTER:'false'},'true').blocker,'deployment_disabled');
 assert.equal(converterAdmission({...env,QUORIVIO_WORKER_TOKEN:'short'},'true').blocker,'worker_configuration_missing');
 assert.equal(converterAdmission({...env,QUORIVIO_CONVERTER_WORKER_URL:'https://evil.invalid/'},'true').enabled,false);
 assert.equal(converterDeploymentConfigured({...env,QUORIVIO_WORKER_TOKEN:'REPLACE_WITH_32_PLUS_RANDOM_CHARACTERS'}),false);
 assert.equal(converterAdmission(env,'false').blocker,'disabled_by_admin');
 assert.equal(converterAdmission(env,'true').enabled,true);
});
test('administrative runtime switch accepts strict boolean only',()=>{
 assert.equal(validConverterToggle({enabled:true}),true);
 assert.equal(validConverterToggle({enabled:false}),true);
 for(const input of [null,[],{},'true',{enabled:'true'},{enabled:1},{enabled:false,token:'secret'}])assert.equal(validConverterToggle(input),false);
});
