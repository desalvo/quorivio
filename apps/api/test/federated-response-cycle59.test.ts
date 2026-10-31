import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {boundedFederatedJson} from '../src/federated-response.js';
import {exchangeSocialCode,socialSubject} from '../src/social-oauth.ts';
import {fetchOidcJson} from '../src/oidc.ts';

const json = (value: unknown) => new Response(JSON.stringify(value));
test('valid bounded provider object and UTF-8 multibyte decoded losslessly',async()=>{
 assert.deepEqual(await boundedFederatedJson(json({name:'Città',valid:true}),200),{name:'Città',valid:true});
});
test('rejects wrong response budgets and scalar/array provider JSON',async()=>{
 for(const n of [0,-1,1.5,300000])await assert.rejects(boundedFederatedJson(json({}),n),RangeError);
 for(const invalid of [null,[],[1],true,'string',123])await assert.rejects(boundedFederatedJson(json(invalid),100),/federated_invalid_json/);
});
test('rejects declared oversized body before reading stream',async()=>{
 let pulled=false;
 const body=new ReadableStream({pull(c){pulled=true;c.enqueue(new Uint8Array([123,125]));c.close();}});
 const response=new Response(body,{headers:{'content-length':'2000'}});
 await assert.rejects(boundedFederatedJson(response,32),/too_large/);
 assert.equal(response.bodyUsed,false); // Streams may prefetch, but the decoder must not acquire the reader.
});
test('stops streaming oversized response and cancels reader without buffering rest',async()=>{
 let delivered=0,cancelled=false;
 const stream=new ReadableStream<Uint8Array>({
  pull(controller){delivered++;controller.enqueue(new Uint8Array(40).fill(65));},
  cancel(){cancelled=true;}
 });
 await assert.rejects(boundedFederatedJson(new Response(stream),60),/too_large/);
 assert.equal(cancelled,true);
 assert.ok(delivered<8,'must stop instead of exhausting an unlimited provider stream');
});
test('rejects invalid UTF-8 and non-JSON provider response',async()=>{
 await assert.rejects(boundedFederatedJson(new Response(new Uint8Array([123,34,120,34,58,34,255,34,125])),100),/invalid_json/);
 await assert.rejects(boundedFederatedJson(new Response('<html>redirect</html>'),100),/invalid_json/);
});
test('rejects JSON whose UTF-8 byte size exceeds maximum regardless of character count',async()=>{
 const response=json({name:'é'.repeat(90)});
 await assert.rejects(boundedFederatedJson(response,120),/too_large/);
});
test('OAuth token exchange fails closed on large streamed untrusted provider reply',async()=>{
 const old=globalThis.fetch;
 globalThis.fetch=async()=>json({access_token:'a'.repeat(9000)});
 try{
  await assert.rejects(exchangeSocialCode({id:'github',clientId:'cid',clientSecret:'secret',redirectUri:'https://app.test/api/auth/social/github/callback'},'code'),/too_large/);
 }finally{globalThis.fetch=old}
});
test('Social identity refuses oversized provider JSON before accessing id',async()=>{
 const old=globalThis.fetch;
 globalThis.fetch=async()=>json({id:'1234',extra:'a'.repeat(17000)});
 try{
  await assert.rejects(socialSubject({id:'facebook',clientId:'cid',clientSecret:'secret',redirectUri:'https://app.test/api/auth/social/facebook/callback'},'token'),/too_large/);
 }finally{globalThis.fetch=old}
});
test('OIDC discovery/JWKS reader rejects oversized provider reply early',async()=>{
 const old=globalThis.fetch;
 globalThis.fetch=async()=>json({issuer:'https://idp.test',extra:'a'.repeat(263000)});
 try{
  await assert.rejects(fetchOidcJson('https://idp.test/.well-known/openid-configuration'),/too_large/);
 }finally{globalThis.fetch=old}
});
