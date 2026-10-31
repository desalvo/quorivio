import test from 'node:test';
import assert from 'node:assert/strict';
import {createLivePeriodicRefresh} from '../src/live-periodic-refresh.ts';
import {createLiveConnection,type LiveSocket,type LiveRuntime} from '../../web/src/live-connection.ts';

class FakeSocket implements LiveSocket {
 readyState=0;
 closes=0;
 onopen:((event:Event)=>void)|null=null;
 onclose:((event:CloseEvent)=>void)|null=null;
 onerror:((event:Event)=>void)|null=null;
 onmessage:((event:MessageEvent)=>void)|null=null;
 open(){this.readyState=1;this.onopen?.({} as Event)}
 deliver(sessionId:string){this.onmessage?.({data:JSON.stringify({type:'snapshot',data:{session:{id:sessionId}}})} as MessageEvent)}
 close(){this.closes++;this.readyState=3;this.onclose?.({code:1006} as CloseEvent)}
}
function simulate(){
 let now=0,id=1;
 const pending=new Map<number,{at:number,fn:()=>void}>();
 const sockets:FakeSocket[]=[];
 const statuses:string[]=[];
 let applied=0;
 const runtime:LiveRuntime={createSocket:()=>{const s=new FakeSocket();sockets.push(s);return s},isOnline:()=>true,
  schedule:(fn,ms)=>{const n=id++;pending.set(n,{at:now+ms,fn});return n},cancel:n=>{pending.delete(n)}};
 const transport=createLiveConnection({sessionId:'private-A',url:'wss://localhost/live?session=private-A',runtime,snapshotTimeoutMs:65000,random:()=>0.5,
  onSnapshot:()=>applied++,onConnection:s=>statuses.push(s)});
 sockets[0].open();
 const advance=(ms:number)=>{const until=now+ms;for(let i=0;i<2000;i++){
  const next=[...pending.entries()].filter(([,t])=>t.at<=until).sort((a,b)=>a[1].at-b[1].at)[0];
  if(!next){now=until;return}
  const [n,t]=next;pending.delete(n);now=t.at;t.fn();
 }throw new Error('unexpected timer storm')};
 return {sockets,statuses,pending,transport,advance,applied:()=>applied};
}

test('RC56 integrated: quiet sessions stay connected for ten minutes with authoritative 20s snapshots',async()=>{
 const h=simulate();let dbReads=0;
 const pump=createLivePeriodicRefresh({activeSessions:()=>['private-A'],readAndSend:async sid=>{
  dbReads++;h.sockets.at(-1)?.deliver(sid);
 }});
 for(let t=0;t<600000;t+=20000){h.advance(20000);await pump.tick()}
 assert.equal(dbReads,30);assert.equal(h.applied(),30);
 assert.equal(h.sockets.length,1,'a healthy idle session must never reconnect');
 assert.deepEqual(h.statuses,['connecting','connected']);
 h.transport.dispose();assert.equal(h.pending.size,0);
});
test('RC56 integrated: lost database snapshots eventually force a fenced reconnect',async()=>{
 const h=simulate();let dbAvailable=true;
 const pump=createLivePeriodicRefresh({activeSessions:()=>['private-A'],readAndSend:async sid=>{
  if(!dbAvailable)throw new Error('database unavailable');h.sockets.at(-1)?.deliver(sid);
 }});
 h.advance(20000);await pump.tick();dbAvailable=false;
 for(let i=0;i<3;i++){h.advance(20000);await pump.tick()}
 h.advance(5000);assert.equal(h.sockets[0].closes,1);
 assert.equal(h.statuses.at(-1),'disconnected');
 h.advance(1800);assert.equal(h.sockets.length,2);
 h.sockets[1].open();
 h.sockets[0].deliver('private-A');assert.equal(h.applied(),1,'late old socket must be ignored');
 dbAvailable=true;await pump.tick();assert.equal(h.applied(),2);
 h.transport.dispose();
});
test('RC56 integrated: cross-session data cannot renew an idle transport',async()=>{
 const h=simulate();
 const pump=createLivePeriodicRefresh({activeSessions:()=>['private-B'],readAndSend:async sid=>h.sockets[0].deliver(sid)});
 for(let i=0;i<3;i++){h.advance(20000);await pump.tick()}
 assert.equal(h.applied(),0);
 h.advance(5000);assert.equal(h.sockets[0].closes,1);
 h.transport.dispose();
});
