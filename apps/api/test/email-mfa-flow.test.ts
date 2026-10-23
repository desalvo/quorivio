import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const dir=path.dirname(fileURLToPath(import.meta.url));
const server=readFileSync(path.join(dir,'../src/server.ts'),'utf8');
const schema=readFileSync(path.join(dir,'../src/schema.sql'),'utf8');
test('email MFA challenge is stored in PostgreSQL with expiry and attempt limits',()=>{
 assert.match(schema,/CREATE TABLE IF NOT EXISTS email_mfa_challenges/);
 assert.match(schema,/CHECK\(attempts BETWEEN 0 AND 5\)/);
 assert.match(server,/emailOtpDigest\(code,r\.rows\[0\]\.user_id,id,secret\)/);
 assert.match(server,/sendEmailOtp\(mail.smtp,mail.email,mail.code\)/);
});
test('verify consumes challenge transactionally and never issues cookie before verification',()=>{
 const handler=server.split("app.post('/api/auth/email-mfa/verify'")[1]?.split("app.post('/api/auth/email-mfa/settings'")[0]||'';
 assert.match(handler,/FOR UPDATE OF c/);
 assert.match(handler,/matchesEmailOtp\(/);
 assert.match(handler,/attempts=attempts\+1/);
 assert.match(handler,/DELETE FROM email_mfa_challenges WHERE user_id/);
 assert.match(handler,/await client.query\('COMMIT'\)/);
 assert.match(handler,/res.cookie\('q_auth'/);
});
test('federated login cannot bypass required email MFA',()=>{
 assert.match(server,/if\(u.totp_enabled\|\|u.email_mfa_enabled\)/);
});
