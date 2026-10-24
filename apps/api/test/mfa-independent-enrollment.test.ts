import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const dir=path.dirname(fileURLToPath(import.meta.url));
const server=readFileSync(path.join(dir,'../src/server.ts'),'utf8');

test('authenticator enrollment does not require SMTP and protects provisioning secret',()=>{
 const setup=server.split("app.post('/api/auth/mfa/setup'")[1]?.split("app.get('/api/auth/mfa/qr'")[0]||'';
 assert.ok(setup.includes('generateTotpSecret()'));
 assert.doesNotMatch(setup,/activeSmtpConfig|smtp_required_before_mfa/);
 assert.match(setup,/Cache-Control','no-store, private'/);
 assert.match(setup,/totp_pending_secret/);
});
test('email MFA still explicitly requires configured SMTP',()=>{
 const settings=server.split("app.post('/api/auth/email-mfa/settings'")[1]?.split("app.get('/api/auth/me'")[0]||'';
 assert.match(settings,/activeSmtpConfig\(\)/);
 assert.match(settings,/smtp_required_before_email_mfa/);
});

test('email factor enrollment is proof-of-inbox before account MFA activation',()=>{
 const settings=server.split("app.post('/api/auth/email-mfa/settings'")[1]?.split("app.post('/api/auth/email-mfa/enrollment/confirm'")[0]||'';
 const confirm=server.split("app.post('/api/auth/email-mfa/enrollment/confirm'")[1]?.split("app.get('/api/auth/me'")[0]||'';
 const schema=readFileSync(path.join(dir,'../src/schema.sql'),'utf8');
 assert.match(schema,/CREATE TABLE IF NOT EXISTS email_mfa_enrollments/);
 assert.match(schema,/attempts integer NOT NULL DEFAULT 0 CHECK\(attempts BETWEEN 0 AND 5\)/);
 assert.match(settings,/sendEmailOtp\(smtp,r\.rows\[0\]\.email,code\)/);
 assert.match(settings,/pending_confirmation:true/);
 assert.doesNotMatch(settings.split('if(enabled){')[1]?.split('const cx=')[0]||'',/email_mfa_enabled=true/);
 assert.match(confirm,/FOR UPDATE/);
 assert.match(confirm,/matchesEmailOtp/);
 assert.match(confirm,/attempts=attempts\+1/);
 assert.match(confirm,/email_mfa_enabled=true,auth_revoked_at=now\(\)/);
 assert.match(confirm,/DELETE FROM email_mfa_enrollments WHERE user_id/);
});
