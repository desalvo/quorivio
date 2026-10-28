import {test} from 'node:test';import {strict as assert} from 'node:assert';
import {socialProviders,socialState,socialAuthorizationUrl,validSocialSubject,facebookAppSecretProof} from '../src/social-oauth.ts';
const github={id:'github' as const,clientId:'id',clientSecret:'secret',redirectUri:'https://quorivio.example.org/api/auth/social/github/callback'};
test('social configuration rejects incomplete and insecure provider',()=>{assert.deepEqual(socialProviders({}),[]);assert.equal(socialProviders({OAUTH_GITHUB_CLIENT_ID:'id',OAUTH_GITHUB_CLIENT_SECRET:'secret',OAUTH_GITHUB_REDIRECT_URI:'http://bad.example.org'}).length,0);assert.equal(socialProviders({OAUTH_GITHUB_CLIENT_ID:'id',OAUTH_GITHUB_CLIENT_SECRET:'secret',OAUTH_GITHUB_REDIRECT_URI:github.redirectUri}).length,1)});
test('social state is unpredictable and URL contains state and callback',()=>{const x=socialState(),y=socialState();assert.notEqual(x,y);assert.ok(x.length>=40);const u=new URL(socialAuthorizationUrl(github,x));assert.equal(u.hostname,'github.com');assert.equal(u.searchParams.get('state'),x);assert.equal(u.searchParams.get('redirect_uri'),github.redirectUri)});
test('facebook authorization URL has restricted scope',()=>{const p={...github,id:'facebook' as const};const u=new URL(socialAuthorizationUrl(p,'test'));assert.equal(u.hostname,'www.facebook.com');assert.equal(u.searchParams.get('scope'),'public_profile,email')});
test('subjects only accept immutable decimal provider identifiers',()=>{assert.equal(validSocialSubject(123),'123');assert.equal(validSocialSubject('0005'),'0005');for(const id of ['abc','',null,'a.b','-1'])assert.equal(validSocialSubject(id),null)});
test('Facebook proof is HMAC not a raw secret',()=>{assert.match(facebookAppSecretProof('token','secret'),/^[0-9a-f]{64}$/);assert.notEqual(facebookAppSecretProof('a','secret'),facebookAppSecretProof('b','secret'))});

// A provider integration must never disclose OAuth secrets in a URL, even to a
// legitimate provider: URLs are routinely recorded by reverse proxies.
test('social provider callbacks must match the configured provider and contain no query',()=>{
 const env={OAUTH_GITHUB_CLIENT_ID:'id',OAUTH_GITHUB_CLIENT_SECRET:'secret',OAUTH_GITHUB_REDIRECT_URI:github.redirectUri};
 assert.equal(socialProviders(env).length,1);
 for(const redirect of [
  'https://quorivio.example.org/api/auth/social/facebook/callback',
  github.redirectUri+'?next=1',
  github.redirectUri+'#fragment',
  'https://attacker.example.org/redirect'
 ]){
  if(redirect==='https://attacker.example.org/redirect'){
   // The hostname is deployment-defined; the strict path is what matters.
  }
  assert.equal(socialProviders({...env,OAUTH_GITHUB_REDIRECT_URI:redirect}).length,0);
 }
});

test('Facebook token exchange uses POST, never redirects or query-string secrets',async()=>{
 const {exchangeSocialCode}=await import('../src/social-oauth.ts');
 const p={...github,id:'facebook' as const};
 const original=globalThis.fetch;const calls:Array<{url:string;init:RequestInit}> = [];
 globalThis.fetch=async (url,init)=>{
  calls.push({url:String(url),init:init||{}});
  return new Response(JSON.stringify({access_token:'facebook-access-token'}),{status:200});
 };
 try{
  const token=await exchangeSocialCode(p,'one-time-code');
  assert.equal(token,'facebook-access-token');
  assert.equal(calls.length,1);
  const call=calls[0];assert.equal(new URL(call.url).search,'');
  assert.equal(call.init.method,'POST');assert.equal(call.init.redirect,'error');
  const body=call.init.body as URLSearchParams;
  assert.equal(body.get('code'),'one-time-code');assert.equal(body.get('client_secret'),'secret');
 }finally{globalThis.fetch=original}
});

test('social identity requests use Authorization header without URL access token',async()=>{
 const {socialSubject}=await import('../src/social-oauth.ts');
 const p={...github,id:'facebook' as const};
 const original=globalThis.fetch;const calls:Array<{url:string;init:RequestInit}> = [];
 globalThis.fetch=async (url,init)=>{calls.push({url:String(url),init:init||{}});return new Response('{"id":"12345"}',{status:200})};
 try{
  assert.equal(await socialSubject(p,'top-secret-facebook-token'),'12345');
  const call=calls[0];const url=new URL(call.url);
  assert.equal(url.searchParams.has('access_token'),false);
  assert.equal(url.searchParams.get('appsecret_proof'),facebookAppSecretProof('top-secret-facebook-token','secret'));
  assert.equal((call.init.headers as Record<string,string>).authorization,'Bearer top-secret-facebook-token');
  assert.equal(call.init.redirect,'error');
 }finally{globalThis.fetch=original}
});
