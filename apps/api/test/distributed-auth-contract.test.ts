import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
const root=new URL('../src/',import.meta.url);
const source=readFileSync(new URL('server.ts',root),'utf8');
const schema=readFileSync(new URL('schema.sql',root),'utf8');
test('federated state is single-use through database DELETE RETURNING on callbacks',()=>{
 assert.match(source,/DELETE FROM auth_flows WHERE state_hash=\$1 AND kind='oidc' AND expires_at>now\(\) RETURNING/);
 assert.match(source,/DELETE FROM auth_flows WHERE state_hash=\$1 AND kind='social' AND expires_at>now\(\) RETURNING/);
 assert.doesNotMatch(source,/oidcPending\.get|socialPending\.get/);
});
test('authorization flows keep provider identity and expire after five minutes',()=>{
 assert.match(schema,/CREATE TABLE IF NOT EXISTS auth_flows/);
 assert.match(schema,/state_hash text PRIMARY KEY/);
 assert.match(source,/now\(\)\+interval '5 minutes'/);
});
test('rate limit is cross-replica and fails closed on database errors',()=>{
 assert.match(schema,/CREATE TABLE IF NOT EXISTS api_rate_windows/);
 assert.match(source,/ON CONFLICT\(client_hash,bucket\) DO UPDATE SET hits=api_rate_windows.hits\+1/);
 assert.match(source,/rate_limiter_unavailable/);
 assert.doesNotMatch(source,/const attempts=new Map/);
});
