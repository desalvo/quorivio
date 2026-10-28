import {test} from 'node:test';import {strict as assert} from 'node:assert';import {generateKeyPairSync,sign} from 'node:crypto';
import {pkceChallenge,authorizationUrl,validProvider,validateDiscovery,validateClaims,verifyIdToken,providersFromEnv} from '../src/oidc.ts';
const p={id:'university',issuer:'https://identity.example.org',clientId:'quorivio',clientSecret:'secret',redirectUri:'https://app.example.org/api/auth/oidc/university/callback'};
const d={issuer:p.issuer,authorization_endpoint:p.issuer+'/authorize',token_endpoint:p.issuer+'/token',jwks_uri:p.issuer+'/jwks'};
test('PKCE SHA256 and state are encoded correctly',()=>{const u=new URL(authorizationUrl(p,d,'state','challenge','nonce'));assert.equal(u.searchParams.get('code_challenge_method'),'S256');assert.equal(u.searchParams.get('state'),'state');assert.equal(u.searchParams.get('nonce'),'nonce');assert.equal(pkceChallenge('hello'), 'LPJNul-wow4m6DsqxbninhsWHlwfp0JecwQzYpOLmCQ')});
test('OIDC configuration must be HTTPS',()=>{assert.equal(validProvider(p),true);assert.equal(validProvider({...p,issuer:'http://identity.example.org'}),false);assert.equal(providersFromEnv({}).length,0);assert.throws(()=>validateDiscovery(p,{...d,issuer:'https://attacker.invalid'}))});
test('claims enforce audience, issuer, nonce and verified email',()=>{const c={iss:p.issuer,aud:p.clientId,exp:3000,iat:1000,nonce:'0123456789abcdefghijklmno',sub:'u1',email:'PERSON@example.org',email_verified:true};assert.equal(validateClaims(c,p,'0123456789abcdefghijklmno',1100).email,'person@example.org');assert.throws(()=>validateClaims({...c,email_verified:false},p,'0123456789abcdefghijklmno',1100));assert.throws(()=>validateClaims({...c,nonce:'other'},p,'0123456789abcdefghijklmno',1100));assert.throws(()=>validateClaims({...c,aud:'other'},p,'0123456789abcdefghijklmno',1100));});
test('RS256 token verified using provider JWKS',async()=>{const {privateKey,publicKey}=generateKeyPairSync('rsa',{modulusLength:2048});const pub=publicKey.export({format:'jwk'});const b=(v:unknown)=>Buffer.from(JSON.stringify(v)).toString('base64url');const head=b({alg:'RS256',kid:'main'}),body=b({iss:p.issuer,aud:p.clientId,exp:3000,iat:1000,nonce:'0123456789abcdefghijklmno',sub:'user',email:'x@example.org',email_verified:true});const content=head+'.'+body,signature=sign('RSA-SHA256',Buffer.from(content),privateKey).toString('base64url');const jwks={keys:[{...pub,kid:'main',use:'sig'}]};assert.equal((await verifyIdToken(content+'.'+signature,p,'0123456789abcdefghijklmno',jwks,1100)).subject,'user');await assert.rejects(verifyIdToken(content+'.'+signature.slice(2)+'xx',p,'0123456789abcdefghijklmno',jwks,1100));await assert.rejects(verifyIdToken(content+'.'+signature,p,'different',jwks,1100))});

test('generic provider registration accepts multiple configured OIDC providers',()=>{const env={OIDC_PROVIDERS_JSON:JSON.stringify([{id:'university',label:'University Login',issuer:'https://identity.example.org',clientId:'client',clientSecret:'secret',redirectUri:'https://app.example.org/api/auth/oidc/university/callback'},{id:'partner',issuer:'https://login.example.org',clientId:'client2',clientSecret:'secret2',redirectUri:'https://app.example.org/api/auth/oidc/partner/callback'}])};const list=providersFromEnv(env);assert.equal(list.length,2);assert.equal(list[0].label,'University Login');assert.equal(list[1].id,'partner')});
test('generic providers reject unsafe IDs, duplicates and callback mismatches',()=>{const base={id:'partner',issuer:'https://login.example.org',clientId:'client',clientSecret:'secret',redirectUri:'https://app.example.org/api/auth/oidc/partner/callback'};for(const item of [{...base,id:'github'},{...base,id:'BAD'}, {...base,redirectUri:'https://app.example.org/api/auth/oidc/another/callback'},{...base,label:'<script>'}])assert.throws(()=>providersFromEnv({OIDC_PROVIDERS_JSON:JSON.stringify([item])}));assert.throws(()=>providersFromEnv({OIDC_PROVIDERS_JSON:JSON.stringify([base,base])}));assert.throws(()=>providersFromEnv({OIDC_PROVIDERS_JSON:'invalid'}))});

test('OIDC rejects implausibly old or oversized validity intervals',()=>{const c={iss:p.issuer,aud:p.clientId,exp:3000,iat:1000,nonce:'0123456789abcdefghijklmno',sub:'u1',email:'a@example.org',email_verified:true};assert.throws(()=>validateClaims({...c,iat:-100000},p,c.nonce,1100));assert.throws(()=>validateClaims({...c,exp:900000},p,c.nonce,1100));assert.throws(()=>validateClaims({...c,exp:Infinity},p,c.nonce,1100));assert.throws(()=>validateClaims(c,p,'short',1100));});

test('OIDC legacy callback route is fixed and issuer cannot carry queries',()=>{
 const env={OIDC_GOOGLE_ISSUER:'https://accounts.google.com',OIDC_GOOGLE_CLIENT_ID:'client',OIDC_GOOGLE_CLIENT_SECRET:'secret',OIDC_GOOGLE_REDIRECT_URI:'https://quorivio.example.org/api/auth/oidc/google/callback'};
 assert.equal(providersFromEnv(env).length,1);
 assert.equal(providersFromEnv({...env,OIDC_GOOGLE_REDIRECT_URI:'https://quorivio.example.org/api/auth/oidc/custom/callback'}).length,0);
 assert.equal(providersFromEnv({...env,OIDC_GOOGLE_REDIRECT_URI:env.OIDC_GOOGLE_REDIRECT_URI+'?next=1'}).length,0);
 assert.equal(providersFromEnv({...env,OIDC_GOOGLE_ISSUER:'https://accounts.google.com/?bad=1'}).length,0);
});

test('OIDC discovery rejects credential-bearing and fragment endpoints',()=>{
 for(const endpoint of ['https://user:secret@idp.example.org/token','https://idp.example.org/token#key','http://idp.example.org/token']){
  assert.throws(()=>validateDiscovery(p,{...d,token_endpoint:endpoint}));
 }
});

test('OIDC discovery fetch disallows redirects before decoding provider JSON',async()=>{
 const {fetchOidcJson}=await import('../src/oidc.ts');
 const old=globalThis.fetch;
 let redirectMode='';
 globalThis.fetch=async (_url,options)=>{
  redirectMode=String(options?.redirect);
  return new Response('{"issuer":"https://identity.example.org"}',{status:200});
 };
 try{
  assert.deepEqual(await fetchOidcJson('https://idp.example.org/.well-known/openid-configuration'),{issuer:'https://identity.example.org'});
  assert.equal(redirectMode,'error');
  await assert.rejects(fetchOidcJson('http://idp.example.org/config'));
 }finally{globalThis.fetch=old}
});
