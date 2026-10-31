import test from 'node:test';
import assert from 'node:assert/strict';
import {createLiveConnection,jitteredLiveRetryMs,type LiveSocket} from '../src/live-connection.ts';
import type {LiveRuntime} from '../src/live-connection.ts';

class ControlledSocket implements LiveSocket {
 readyState=0;
 onopen:((event:Event)=>void)|null=null;
 onclose:((event:CloseEvent)=>void)|null=null;
 onerror:((event:Event)=>void)|null=null;
 onmessage:((event:MessageEvent)=>void)|null=null;
 closes=0;
 open(){this.readyState=1;this.onopen?.({} as Event)}
 receive(data:unknown){this.onmessage?.({data:JSON.stringify(data)} as MessageEvent)}
 close(code=1006){this.closes++;this.readyState=3;this.onclose?.({code} as CloseEvent)}
}
function harness(online=true){
 let active=online;
 let clock=0;
 let next=1;
 const sockets:ControlledSocket[]=[];
 const timers=new Map<number,{at:number,callback:()=>void}>();
 const statuses:string[]=[];
 const snapshots:unknown[]=[];
 const runtime:LiveRuntime={
  createSocket:()=>{const s=new ControlledSocket();sockets.push(s);return s},
  isOnline:()=>active,
  schedule:(callback,ms)=>{const id=next++;timers.set(id,{at:clock+ms,callback});return id},
  cancel:id=>{timers.delete(id)},
 };
 const connection=createLiveConnection({sessionId:'one',url:'wss://example.org/live?session=one',runtime,random:()=>0.5,
  onConnection:s=>statuses.push(s),onSnapshot:s=>snapshots.push(s)});
 const tick=(delta:number)=>{
  const stop=clock+delta;
  for(let k=0;k<200;k++){
   const pending=[...timers.entries()].filter(([,t])=>t.at<=stop).sort((a,b)=>a[1].at-b[1].at);
   if(!pending.length){clock=stop;return}
   const [id,t]=pending[0];timers.delete(id);clock=t.at;t.callback();
  }
  throw new Error('unexpected repeated timers');
 };
 return {sockets,timers,statuses,snapshots,connection,tick,setOnline:(v:boolean)=>{active=v;v?connection.online():connection.offline()}};
}
const snapshot=(id='one')=>({type:'snapshot',data:{session:{id},totals:[]}});

test('initial live connection sends only the expected session and drops invalid payloads',()=>{
 const h=harness();assert.equal(h.sockets.length,1);assert.deepEqual(h.statuses,['connecting']);
 const s=h.sockets[0];s.open();assert.deepEqual(h.statuses,['connecting','connected']);
 s.receive(snapshot('other'));s.receive(snapshot());s.onmessage?.({data:'not-json'} as MessageEvent);
 assert.equal(h.snapshots.length,1);h.connection.dispose();
});
test('network outage fences previous socket and reconnects only once after online',()=>{
 const h=harness();const old=h.sockets[0];old.open();
 h.setOnline(false);assert.equal(old.closes,1);assert.equal(h.timers.size,0);
 h.setOnline(true);h.setOnline(true);assert.equal(h.sockets.length,2);
 h.sockets[1].open();old.onclose?.({code:1008} as CloseEvent);old.receive(snapshot());
 assert.equal(h.statuses.at(-1),'connected');assert.equal(h.snapshots.length,0);
 h.sockets[1].receive(snapshot());assert.equal(h.snapshots.length,1);h.connection.dispose();
});
test('retry uses bounded delay and resets after successful connection',()=>{
 const h=harness();h.sockets[0].close();assert.deepEqual(h.statuses,['connecting','disconnected']);
 h.tick(1799);assert.equal(h.sockets.length,1);h.tick(1);assert.equal(h.sockets.length,2);
 h.sockets[1].open();h.sockets[1].close();h.tick(1800);assert.equal(h.sockets.length,3);
 assert.equal(jitteredLiveRetryMs(0,0),1440);assert.equal(jitteredLiveRetryMs(0,1),2160);
 assert.ok(jitteredLiveRetryMs(99,1)<=30000);h.connection.dispose();
});
test('server authorization close codes are terminal across online toggles',()=>{
 for(const code of [4003,1008]){
  const h=harness();h.sockets[0].open();h.sockets[0].close(code);
  h.tick(100000);h.setOnline(false);h.setOnline(true);
  assert.equal(h.sockets.length,1,`code ${code} should not reconnect`);
  assert.equal(h.timers.size,0);assert.equal(h.statuses.at(-1),'blocked');h.connection.dispose();
 }
});
test('a stuck handshake is abandoned and recovered without accepting stale events',()=>{
 const h=harness();const old=h.sockets[0];h.tick(15000);
 assert.equal(old.closes,1);assert.equal(h.statuses.at(-1),'disconnected');
 h.tick(1800);assert.equal(h.sockets.length,2);
 h.sockets[1].open();old.open();old.receive(snapshot());
 assert.equal(h.statuses.at(-1),'connected');assert.equal(h.snapshots.length,0);h.connection.dispose();
});
test('disposed transport cancels pending timers and rejects old events',()=>{
 const h=harness();const s=h.sockets[0];h.connection.dispose();
 s.open();s.receive(snapshot());h.tick(100000);h.setOnline(true);
 assert.equal(h.sockets.length,1);assert.equal(h.snapshots.length,0);assert.equal(h.timers.size,0);
});
test('socket construction failure recovers through a single bounded retry',()=>{
 const h=harness();h.connection.dispose();
 let calls=0;let next=1;const timers=new Map<number,()=>void>();const statuses:string[]=[];
 const c=createLiveConnection({sessionId:'one',url:'wss://example.org/live',runtime:{
  createSocket:()=>{calls++;throw Error('network denied')},isOnline:()=>true,
  schedule:(f)=>{const id=next++;timers.set(id,f);return id},cancel:id=>{timers.delete(id)}},
  onSnapshot:()=>{},onConnection:s=>statuses.push(s)});
 assert.equal(calls,1);assert.equal(timers.size,1);
 const [firedId,fired]=[...timers.entries()][0];timers.delete(firedId);fired();assert.equal(calls,2);assert.equal(timers.size,1);
 c.dispose();assert.equal(timers.size,0);
});
test('error of a retired socket never closes a newer connection',()=>{
 const h=harness();const old=h.sockets[0];old.open();h.setOnline(false);h.setOnline(true);
 const fresh=h.sockets[1];fresh.open();old.onerror?.({} as Event);
 assert.equal(fresh.closes,0);assert.equal(h.statuses.at(-1),'connected');h.connection.dispose();
});

test('loading a live page while already offline reports disconnected and resumes once',()=>{
 const h=harness(false);
 assert.deepEqual(h.statuses,['disconnected']); // explicit initial offline state
 assert.equal(h.sockets.length,0);
 h.setOnline(true);assert.equal(h.sockets.length,1);
 h.sockets[0].open();assert.equal(h.statuses.at(-1),'connected');h.connection.dispose();
});
