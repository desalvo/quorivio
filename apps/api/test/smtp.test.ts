import {test} from 'node:test';import {strict as assert} from 'node:assert';
import {smtpConfigFromEnv,smtpPublicSettings} from '../src/smtp.ts';
test('SMTP absent by default',()=>assert.equal(smtpConfigFromEnv({}),null));
test('SMTPS settings require TLS and credentials',()=>{assert.throws(()=>smtpConfigFromEnv({SMTP_HOST:'mail.example.org',SMTP_USER:'abc',SMTP_PASSWORD:'secret',SMTP_FROM:'from@example.org',SMTP_SECURE:'false'}));assert.throws(()=>smtpConfigFromEnv({SMTP_HOST:'mail.example.org'}))});
test('SMTP credentials excluded from public status',()=>{const env={SMTP_HOST:'mail.example.org',SMTP_PORT:'465',SMTP_USER:'abc',SMTP_PASSWORD:'TOPSECRET',SMTP_FROM:'from@example.org'};const status=smtpPublicSettings(env);assert.equal(status.configured,true);assert.ok(!JSON.stringify(status).includes('TOPSECRET'))});
