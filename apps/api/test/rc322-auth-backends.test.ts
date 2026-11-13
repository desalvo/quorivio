import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ldapSettingsFromEnv} from '../src/ldap-auth.ts';
const source=readFileSync(new URL('../src/auth-backends.ts',import.meta.url),'utf8');
const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
test('external backends fail closed by default even with legacy credentials',()=>{
 for(const kind of ['ldap','google','github','facebook'])assert.match(source,new RegExp("id:'"+kind+"',kind:'[^']+',enabled:false"));
 assert.match(source,/id:'local',kind:'local',enabled:true/);
 assert.match(source,/enabled:kind==='local'\?true:row\.enabled===true/);
 assert.match(server,/enabledOidcBackends\(db,secret\)/);
 assert.match(server,/enabledSocialBackends\(db,secret\)/);
});
test('provider secrets are sealed at rest and omitted from administrative read API',()=>{
 assert.match(source,/createCipheriv\('aes-256-gcm'/);
 assert.match(source,/createDecipheriv\('aes-256-gcm'/);
 assert.match(source,/secretFields=new Set\(\['bindPassword','clientSecret'\]\)/);
 assert.match(source,/Object\.entries\(b\.config\)\.filter\(\(\[k\]\)=>!secretFields\.has\(k\)\)/);
});
test('only LDAP and local users can enroll Quorivio MFA; SSO delegates MFA to IdP',()=>{
 assert.match(server,/enabled===true&&!await backendAllowsMfa/);
 assert.match(server,/if\(!await backendAllowsMfa\(db,secret,uid\)\)/);
 assert.match(source,/backends\.find\(x=>x\.id===id&&x\.enabled\)/);
 assert.match(source,/ldapIdentityKey/);
 assert.doesNotMatch(server,/oidc_mfa_requires_local_login|social_mfa_requires_local_login/);
});
test('insecure LDAP fails closed while StartTLS and LDAPS remain supported',()=>{
 assert.throws(()=>ldapSettingsFromEnv({LDAP_URL:'ldap://ldap.example.org',LDAP_BIND_DN:'cn=svc',LDAP_BIND_PASSWORD:'password',LDAP_BASE_DN:'dc=example'}),/ldap_requires_starttls/);
 assert.throws(()=>ldapSettingsFromEnv({LDAP_URL:'ldaps://ldap.example.org',LDAP_STARTTLS:'true',LDAP_BIND_DN:'cn=svc',LDAP_BIND_PASSWORD:'password',LDAP_BASE_DN:'dc=example'}),/ldaps_cannot_starttls/);
});
