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
