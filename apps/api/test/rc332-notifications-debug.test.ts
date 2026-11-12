import {test} from 'node:test';
import assert from 'node:assert/strict';
import {defaultNoticeConfig,mergeNoticeConfig,publicNoticeConfig} from '../src/notifications.ts';
import {validateDebugSubmission,debugBundlePath} from '../src/debug-submissions.ts';
test('external notification channels are disabled until configured',()=>{
 const settings=defaultNoticeConfig();
 for(const name of ['email','pushover','telegram','whatsapp'] as const)assert.equal(settings.channels[name].enabled,false);
});
test('notifications hide provider credentials from admin UI and keep unchanged tokens',()=>{
 const token='123456789:abcdefghijklmnopqrstuvwxyz1234';
 const stored=mergeNoticeConfig({channels:{telegram:{enabled:true,token}}},defaultNoticeConfig());
 assert.equal(publicNoticeConfig(stored).channels.telegram.token,'');
 assert.equal((publicNoticeConfig(stored).channels.telegram as any).tokenConfigured,true);
 assert.equal(mergeNoticeConfig({channels:{telegram:{token:''}}},stored).channels.telegram.token,token);
});
test('debug archives need separate explicit sharing and diagnostics consent',()=>{
 const report={kind:'bug',message:'Il grafico cambia dimensioni quando arrivano le risposte',consentSubmission:true,consentDiagnostics:false};
 assert.equal(validateDebugSubmission(report).consentDiagnostics,false);
 assert.throws(()=>validateDebugSubmission({...report,consentSubmission:false}),/debug_submission_consent_required/);
 assert.throws(()=>validateDebugSubmission({...report,consentDiagnostics:null}),/debug_diagnostic_consent_required/);
 assert.throws(()=>debugBundlePath('/tmp','../../outside'),/invalid_debug_id/);
});
