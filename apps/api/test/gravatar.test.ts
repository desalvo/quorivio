import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {gravatarHash,gravatarAvatarUrl,downloadGravatar,GRAVATAR_MAX_BYTES} from '../src/gravatar.ts';

const email=' User@Example.Com ';
test('Gravatar uses canonical, lowercase SHA-256 email, not MD5',()=>{
 const expected=createHash('sha256').update('user@example.com').digest('hex');
 assert.equal(gravatarHash(email),expected);
 assert.equal(gravatarAvatarUrl(email),`https://gravatar.com/avatar/${expected}?d=404&s=256&r=g`);
 assert.equal(expected.length,64);
});
test('missing Gravatar is distinguished from default generated avatars',async()=>{
 let called='';
 const fetcher=(async (url:string)=>{called=url;return new Response(null,{status:404})}) as typeof fetch;
 assert.deepEqual(await downloadGravatar(email,fetcher),{status:'missing'});
 assert.match(called,/\?d=404/);
});
test('Gravatar imports image bytes and computes deterministic checksum',async()=>{
 const picture=Buffer.alloc(120);picture[0]=0xff;picture[1]=0xd8;picture[2]=0xff;
 const fetcher=(async()=>new Response(picture,{status:200,headers:{'Content-Type':'image/jpeg','Content-Length':String(picture.length)}})) as typeof fetch;
 const result=await downloadGravatar(email,fetcher);
 assert.equal(result.status,'found');
 if(result.status==='found'){
  assert.equal(result.sha256,createHash('sha256').update(picture).digest('hex'));
  assert.equal(result.mime,'image/jpeg');assert.equal(result.data.length,120);
 }
});
test('remote redirects, HTML responses, excessive files and invalid responses fail closed',async()=>{
 const cases=[
  new Response(null,{status:302,headers:{Location:'http://localhost:8080/private'}}),
  new Response('<html>not an avatar</html>',{status:200,headers:{'Content-Type':'text/html'}}),
  new Response('x',{status:200,headers:{'Content-Type':'image/png','Content-Length':String(GRAVATAR_MAX_BYTES+1)}}),
  new Response(null,{status:500}),
 ];
 for(const result of cases){
  await assert.rejects(()=>downloadGravatar(email,(async()=>result) as typeof fetch));
 }
});
