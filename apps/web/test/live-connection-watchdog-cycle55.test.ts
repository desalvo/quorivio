import test from 'node:test';
import assert from 'node:assert/strict';
import {createLiveConnection,type LiveRuntime,type LiveSocket} from '../src/live-connection.ts';

class ControlledSocket implements LiveSocket {
 readyState=0;
 closes=0;
 onopen:((event:Event)=>void)|null=null;
 onclose:((event:CloseEvent)=>void)|null=null;
 onerror:((event:Event)=>void)|null=null;
 onmessage:((event:MessageEvent)=>void)|null=null;
 open(){this.readyState=1;this.onopen?.({} as Event)}
 send(session='alpha'){this.onmessage?.({data:JSON.stringify({type:'snapshot',data:{session:{id:session}}})} as MessageEvent)}
 close(){this.closes++;this.readyState=3;/* Deliberately no close event: mimic a socket stuck while retiring. */}
}
function fakeRuntime(initialOnline=true){
 let online=initialOnline,now=0,serial=0;
 const sockets:ControlledSocket[]=[];
 const tasks=new Map<number,{due:number,cb:()=>void}>();
 const statuses:string[]=[];
 const snapshots:unknown[]=[];
 const runtime:LiveRuntime={
  createSocket:()=>{const socket=new ControlledSocket();sockets.push(socket);return socket},
  isOnline:()=>online,
  schedule:(cb,ms)=>{const id=++serial;tasks.set(id,{due:now+ms,cb});return id},
  cancel:(id)=>{tasks.delete(id)},
 };
 const transport=createLiveConnection({sessionId:'alpha',url:'wss://example.test/live',runtime,
  random:()=>0.5,snapshotTimeoutMs:5000,
  onConnection:status=>statuses.push(status),onSnapshot:data=>snapshots.push(data)});
 const advance=(ms:number)=>{
  const end=now+ms;
  for(let i=0;i<100;i++){
   const events=[...tasks.entries()].filter(([,v])=>v.due<=end).sort((a,b)=>a[1].due-b[1].due);
   if(!events.length){now=end;return}
   const [id,event]=events[0];tasks.delete(id);now=event.due;event.cb();
  }
  throw new Error('unbounded task cascade');
 };
 return {sockets,tasks,statuses,snapshots,transport,advance,offline:()=>{online=false;transport.offline()},online:()=>{online=true;transport.online()}};
}

test('RC55: an open socket without a valid snapshot is retired and reconnected',()=>{
 const h=fakeRuntime();const first=h.sockets[0];first.open();h.advance(4999);
 assert.equal(first.closes,0);h.advance(1);assert.equal(first.closes,1);
 assert.equal(h.statuses.at(-1),'disconnected');h.advance(1799);assert.equal(h.sockets.length,1);
 h.advance(1);assert.equal(h.sockets.length,2);h.sockets[1].open();
 assert.equal(h.statuses.at(-1),'connected');h.transport.dispose();assert.equal(h.tasks.size,0);
});
test('RC55: only valid same-session snapshots reset the staleness deadline',()=>{
 const h=fakeRuntime();const s=h.sockets[0];s.open();h.advance(4000);
 s.send('alpha');h.advance(4000);
 s.send('wrong-session');s.onmessage?.({data:'not-json'} as MessageEvent);
 assert.equal(h.snapshots.length,1);
 h.advance(999);assert.equal(s.closes,0);h.advance(1);
 assert.equal(s.closes,1);h.transport.dispose();
});
test('RC55: periodic accepted snapshots preserve a live socket past multiple deadlines',()=>{
 const h=fakeRuntime();const s=h.sockets[0];s.open();
 for(let i=0;i<6;i++){h.advance(4000);s.send('alpha')}
 assert.equal(s.closes,0);assert.equal(h.snapshots.length,6);
 assert.deepEqual(h.statuses,['connecting','connected']);h.transport.dispose();
});
test('RC55: going offline cancels stale watchdog, reconnect opens exactly once',()=>{
 const h=fakeRuntime();const old=h.sockets[0];old.open();h.advance(2000);h.offline();
 assert.equal(old.closes,1);assert.equal(h.tasks.size,0);
 h.advance(400000);assert.equal(h.sockets.length,1);
 h.online();h.online();assert.equal(h.sockets.length,2);
 h.sockets[1].open();old.onmessage?.({data:JSON.stringify({type:'snapshot',data:{session:{id:'alpha'}}})} as MessageEvent);
 assert.equal(h.snapshots.length,0);h.transport.dispose();assert.equal(h.tasks.size,0);
});
test('RC55: WebSocket error without a close event still reconnects, with no zombie callback',()=>{
 const h=fakeRuntime();const old=h.sockets[0];old.open();
 old.onerror?.({} as Event);assert.equal(old.closes,1);assert.equal(h.statuses.at(-1),'disconnected');
 h.advance(1800);assert.equal(h.sockets.length,2);h.sockets[1].open();
 old.onclose?.({code:1008} as CloseEvent);
 assert.equal(h.statuses.at(-1),'connected');h.transport.dispose();
});
test('RC55: dispose clears handshake, retry and freshness timers',()=>{
 const h=fakeRuntime();h.sockets[0].open();h.advance(1000);h.transport.dispose();
 assert.equal(h.tasks.size,0);h.advance(300000);assert.equal(h.sockets.length,1);
});
