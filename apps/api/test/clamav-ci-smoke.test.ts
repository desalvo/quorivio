import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:net';
import {stat} from 'node:fs/promises';
import {pingClamd,waitUntilClamdReady,realClamdAcceptance} from '../../../tools/ci_clamav_real.mjs';

async function mockDaemon(reply: string){
 const server=createServer(socket=>socket.on('data',data=>{
  if(data.toString('utf8')==='zPING\0')socket.end(reply);
  else socket.destroy();
 }));
 await new Promise<void>(r=>server.listen(0,'127.0.0.1',r));
 return {server,port:(server.address() as {port:number}).port};
}

test('TCP-open alone is not ClamAV readiness: require exact PONG',async()=>{
 for(const [reply,valid] of [['PONG\0',true],['PENDING\0',false],['PONG\\0',false],['PONG\0bad',false],['',false]] as const){
  const {server,port}=await mockDaemon(reply);
  try{assert.equal(await pingClamd('127.0.0.1',port,500),valid)}
  finally{await new Promise<void>(r=>server.close(()=>r()))}
 }
});

test('readiness retry is bounded and never treats failed PING as ready',async()=>{
 let calls=0,now=0;
 const ok=await waitUntilClamdReady(async()=>++calls===3,{timeoutMs:10000,intervalMs:1000,now:()=>now,sleep:async(ms)=>{now+=ms}});
 assert.equal(ok,true);assert.equal(calls,3);
 calls=0;now=0;
 const denied=await waitUntilClamdReady(async()=>{calls++;return false},{timeoutMs:2500,intervalMs:1000,now:()=>now,sleep:async(ms)=>{now+=ms}});
 assert.equal(denied,false);assert.ok(calls<=4);
});

test('real CI acceptance requires a clean verdict and EICAR rejection',async()=>{
 let count=0;
 const result=await realClamdAcceptance(async(file,env)=>{
  assert.equal(env.NODE_ENV,'production');
  const size=(await stat(file)).size;
  count++;
  if(size===68)throw Error('malware_detected');
  assert.ok(size>0);
 },async()=>true);
 assert.match(result,/PASS real clamd/);assert.equal(count,2);
});

test('unexpected clean failures cannot be reported as detection',async()=>{
 await assert.rejects(realClamdAcceptance(async()=>{throw Error('sensitive secret scanner error')},async()=>true),/clean_scan_unexpected_failure/);
});

test('missing antivirus signature always fails closed',async()=>{
 await assert.rejects(realClamdAcceptance(async()=>{},async()=>true),/eicar_not_detected/);
 await assert.rejects(realClamdAcceptance(async()=>{},async()=>false),/clamd_not_ready/);
});
