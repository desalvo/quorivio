import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
import {FEDERATED_IDENTITY_LIST_SQL,FEDERATED_IDENTITY_UNLINK_SQL,validFederatedProviderId,validFederatedUnlinkPassword} from '../src/federated-identities.ts';
const api=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
const ui=readFileSync(new URL('../../web/src/main.tsx',import.meta.url),'utf8');

test('identity management is always account-scoped and deliberately hides external subjects',()=>{
 assert.match(FEDERATED_IDENTITY_LIST_SQL,/SELECT provider, linked_at FROM oidc_identities WHERE user_id=\$1/);
 assert.match(FEDERATED_IDENTITY_UNLINK_SQL,/DELETE FROM oidc_identities WHERE user_id=\$1 AND provider=\$2 RETURNING provider/);
 assert.doesNotMatch(FEDERATED_IDENTITY_LIST_SQL,/subject|email/);
 assert.doesNotMatch(FEDERATED_IDENTITY_UNLINK_SQL,/subject\s*=/);
});
test('provider and password contracts reject coercion and excess input',()=>{
 for(const id of ['google','github','facebook','my-oidc_2'])assert.equal(validFederatedProviderId(id),true);
 for(const id of ['',null,1,[], 'Google','x','evil:provider','a'.repeat(33),'a\n'])assert.equal(validFederatedProviderId(id),false);
 for(const pw of ['x','a'.repeat(256)])assert.equal(validFederatedUnlinkPassword(pw),true);
 for(const pw of ['',undefined,{},123,'a'.repeat(257)])assert.equal(validFederatedUnlinkPassword(pw),false);
});
test('authenticated API rechecks revocation after locking user row and requires password',()=>{
 assert.match(api,/app\.get\('\/api\/auth\/identities',requireAuth/);
 assert.match(api,/app\.post\('\/api\/auth\/identities\/unlink',requireAuth/);
 assert.match(api,/SELECT password_hash,approved,must_change_password,password_changed_at,auth_revoked_at FROM users WHERE id=\$1 FOR UPDATE/);
 assert.match(api,/await bcrypt\.compare\(password,account\.rows\[0\]\.password_hash\)/);
 assert.match(api,/authCookieIssuedAt\(req\.headers\.cookie\)/);
 assert.match(api,/cx\.query\(FEDERATED_IDENTITY_UNLINK_SQL,\[userId,provider\]\)/);
 assert.match(api,/await cx\.query\('COMMIT'\)/);
});
test('password guessing budget is shared between replicas and survives rollback',()=>{
 const route=api.slice(api.indexOf("app.post('/api/auth/identities/unlink'"),api.indexOf("app.get('/api/auth/me'"));
 assert.match(route,/api_rate_windows/);
 assert.match(route,/hits=api_rate_windows\.hits\+1/);
 assert.match(route,/Number\(attempts\.rows\[0\]\.hits\)>5/);
 assert.ok(route.indexOf('api_rate_windows') < route.indexOf("cx.query('BEGIN')"));
 assert.match(route,/setHeader\('Retry-After'/);
});
test('UI supports listing, confirmation, password challenge, refresh and removal',()=>{
 assert.match(ui,/function FederatedIdentities/);
 assert.match(ui,/request<\{identities:/);
 assert.match(ui,/request\('\/auth\/identities\/unlink','POST',\{provider,password\}\)/);
 assert.match(ui,/autoComplete="current-password"/);
 assert.match(ui,/Conferma scollegamento/);
 assert.match(ui,/setPassword\(''\);setSelected\(''\);await refresh\(\)/);
 assert.match(ui,/dashboardPage==='sso'&&<FederatedIdentities/);
});
