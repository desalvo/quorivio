import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
const schema=readFileSync(new URL('../src/schema.sql',import.meta.url),'utf8');
test('email MFA issuance is limited by shared database counters per account',()=>{
 assert.match(server,/email-mfa-issue:\$\{r\.rows\[0\]\.id\}/);
 assert.match(server,/if\(Number\(issue\.rows\[0\]\.hits\)>3\)/);
 assert.match(server,/email_mfa_rate_limited/);
});
test('only one email MFA challenge per account is retained atomically',()=>{
 assert.match(server,/ON CONFLICT\(user_id\)/);
 assert.match(schema,/CREATE UNIQUE INDEX IF NOT EXISTS uq_email_mfa_challenges_user/);
 assert.match(schema,/DELETE FROM email_mfa_challenges a USING email_mfa_challenges b/);
});
