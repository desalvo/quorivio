import test from 'node:test';import assert from 'node:assert/strict';
import {sealAuthConfig,openAuthConfig,defaultAuthBackends,backendPublic,validateAuthBackend} from '../src/auth-backends.ts';
test('all external backends fail closed despite env credentials; local always enabled',()=>{
 const env={LDAP_URL:'ldaps://ldap.example.org',LDAP_BIND_DN:'cn=svc,dc=example,dc=org',LDAP_BIND_PASSWORD:'redacted',LDAP_BASE_DN:'dc=example,dc=org',
 OIDC_GOOGLE_ISSUER:'https://accounts.google.com',OIDC_GOOGLE_CLIENT_ID:'client',OIDC_GOOGLE_CLIENT_SECRET:'secret',OIDC_GOOGLE_REDIRECT_URI:'https://app.example.org/api/auth/oidc/google/callback',
 OAUTH_GITHUB_CLIENT_ID:'client',OAUTH_GITHUB_CLIENT_SECRET:'secret',OAUTH_GITHUB_REDIRECT_URI:'https://app.example.org/api/auth/social/github/callback'};
 const providers=defaultAuthBackends(env);
 assert.equal(providers.find(x=>x.id==='local')?.enabled,true);
 assert.equal(providers.find(x=>x.id==='ldap')?.enabled,false);
 for(const b of providers.filter(x=>x.kind!=='local'))assert.equal(b.enabled,false,b.id);
});
test('provider credentials use authenticated encryption and are not exposed to admins',()=>{
 const secret='m'.repeat(48),config={label:'Service',clientSecret:'never-leak-this',issuer:'https://idp.example.org'};
 const encrypted=sealAuthConfig(config,secret);
 assert.ok(!encrypted.includes('never-leak-this'));
 assert.deepEqual(openAuthConfig(encrypted,secret),config);
 assert.throws(()=>openAuthConfig(encrypted,secret.slice(1)));
 assert.equal(backendPublic({id:'infn',kind:'oidc',enabled:false,mfaEnabled:false,config,lastTestedAt:null}).config.clientSecret,undefined);
});
test('LDAP requires encrypted transport; SSO cannot accept arbitrary callback or labels',()=>{
 assert.throws(()=>validateAuthBackend('ldap','ldap',{url:'ldap://directory.example.org',bindDn:'cn=svc',bindPassword:'x',baseDn:'dc=example,dc=org'}));
 assert.throws(()=>validateAuthBackend('infn','oidc',{label:'INFN',issuer:'https://idp.example.org',clientId:'a',clientSecret:'b',redirectUri:'https://app.example.org/api/auth/oidc/different/callback'}));
 assert.throws(()=>validateAuthBackend('github','social',{label:'GitHub',clientId:'a',clientSecret:'b',redirectUri:'http://app.example.org/api/auth/social/github/callback'}));
 assert.equal(validateAuthBackend('github','social',{label:'GitHub',clientId:'a',clientSecret:'b',redirectUri:'https://app.example.org/api/auth/social/github/callback'}),true);
});
