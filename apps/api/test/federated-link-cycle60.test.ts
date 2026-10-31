import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
import {
 FEDERATED_LINK_ELIGIBLE_SQL,FEDERATED_LINK_INSERT_SQL,validFederatedLinkIssuedAt,
} from '../src/federated-link.ts';

const source=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
const schema=readFileSync(new URL('../src/schema.sql',import.meta.url),'utf8');

test('link authorization stores signed cookie issuance for each federated provider',()=>{
 assert.equal((source.match(/authorizedFederatedLink\(req\)/g)||[]).length,2);
 assert.match(source,/const userId=auth\(req\),issuedAt=authCookieIssuedAt\(req.headers.cookie\)/);
 assert.match(source,/db.query\(FEDERATED_LINK_ELIGIBLE_SQL,\[userId,issuedAt\]\)/);
 assert.equal((source.match(/link_auth_issued_at_ms,expires_at/g)||[]).length,2);
 assert.equal((source.match(/link\?\.issuedAt\|\|null/g)||[]).length,2);
 assert.match(schema,/ALTER TABLE auth_flows ADD COLUMN IF NOT EXISTS link_auth_issued_at_ms bigint/);
});

test('callback consumes DB state and never trusts an old or missing linking issuance',()=>{
 assert.equal((source.match(/link_auth_issued_at_ms[^\n]*\[hash\(state\)\]/g)||[]).length,2);
 assert.equal((source.match(/validFederatedLinkIssuedAt\(pending.linkIssuedAt\)/g)||[]).length,2);
 assert.equal((source.match(/db.query\(FEDERATED_LINK_INSERT_SQL,\[p.id,/g)||[]).length,2);
 assert.doesNotMatch(source,/oidc_identities\(provider,subject,user_id\) VALUES\(\$1,\$2,\$3\) ON CONFLICT/);
});

test('link start and SQL insertion both reject revoked, rotated, unapproved or locked accounts',()=>{
 for(const predicate of [
  'approved=true','must_change_password=false',
  'auth_revoked_at IS NULL','password_changed_at IS NULL','to_timestamp',
 ]){
  assert.ok(FEDERATED_LINK_ELIGIBLE_SQL.includes(predicate),`start missing ${predicate}`);
  assert.ok(FEDERATED_LINK_INSERT_SQL.includes(predicate),`callback missing ${predicate}`);
 }
 assert.match(FEDERATED_LINK_INSERT_SQL,/INSERT INTO oidc_identities/);
 assert.match(FEDERATED_LINK_INSERT_SQL,/ON CONFLICT DO NOTHING RETURNING user_id/);
});

test('PostgreSQL bigint original issue timestamp is bounded and legacy NULL fails closed',()=>{
 const now=1761885000000;
 assert.equal(validFederatedLinkIssuedAt(String(now-300000),now),now-300000);
 assert.equal(validFederatedLinkIssuedAt(now-300000,now),now-300000);
 for(const invalid of [null,undefined,'',0,'0',' 123','NaN','1.4','-1','999999999999999999999',now+2000,now-8*3600*1000-1]){
  assert.equal(validFederatedLinkIssuedAt(invalid,now),null,`accepted ${String(invalid)}`);
 }
});
