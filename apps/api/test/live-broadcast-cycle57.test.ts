import test from 'node:test';
import assert from 'node:assert/strict';
import {deliverLiveSnapshot, type LiveBroadcastSocket} from '../src/live-broadcast.ts';
import {MAX_LIVE_SOCKET_BUFFER_BYTES,shouldDropSlowSocket} from '../src/live-delivery-policy.ts';

type TestSocket = LiveBroadcastSocket & {view: 'owner'|'audience'; sent: string[]; closed: number[]; throwSend?: boolean};
function socket(view:TestSocket['view'],bufferedAmount=0):TestSocket {
 const s: TestSocket={view,bufferedAmount,readyState:1,sent:[],closed:[],send(p){if(this.throwSend)throw Error('transport');this.sent.push(p)},close(c){this.closed.push(c);this.readyState=3}};
 return s;
}
const audience=(data:any)=>({session:{id:data.session.id},activities:[]});
const send=(clients:TestSocket[],data:unknown,onError=()=>{})=>deliverLiveSnapshot(clients,data,audience,s=>s.view==='owner',shouldDropSlowSocket,onError);

test('500 audience sockets + 1 presenter share exactly two payloads, preserving privacy',()=>{
 const clients=[socket('owner'),...Array.from({length:500},()=>socket('audience'))];
 let serializations=0;
 const data={session:{id:'a'},privateToken:'do-not-leak',toJSON(){serializations++;return {session:this.session,privateToken:this.privateToken}}};
 const result=send(clients,data);
 assert.deepEqual(result,{serialized:2,delivered:501,droppedSlow:0,transportErrors:0});
 assert.equal(serializations,1);
 assert.equal(clients[0].sent.length,1);
 assert.match(clients[0].sent[0],/do-not-leak/);
 assert.equal(new Set(clients.slice(1).map(s=>s.sent[0])).size,1);
 assert.ok(clients.slice(1).every(s=>!s.sent[0].includes('do-not-leak')));
});
test('public-only and owner-only views serialize only the necessary trust domain',()=>{
 assert.equal(send([socket('audience')],{session:{id:'a'}}).serialized,1);
 assert.equal(send([socket('owner')],{session:{id:'a'}}).serialized,1);
 let calls=0;
 assert.equal(deliverLiveSnapshot([socket('owner')],{session:{id:'a'}},()=>{calls++;throw Error('should not run')},s=>s.view==='owner',shouldDropSlowSocket).serialized,1);
 assert.equal(calls,0);
});
test('slow sockets are closed individually, other clients still receive the snapshot',()=>{
 const slow=socket('audience',MAX_LIVE_SOCKET_BUFFER_BYTES);
 const fast=socket('audience');
 const result=send([slow,fast],{session:{id:'a'}});
 assert.equal(result.droppedSlow,1);assert.deepEqual(slow.closed,[1013]);assert.equal(slow.sent.length,0);
 assert.equal(fast.sent.length,1);assert.equal(result.delivered,1);
});
test('a transport failure cannot abort delivery to other sockets',()=>{
 const bad=socket('owner'),good=socket('owner');bad.throwSend=true;
 let errors=0;
 const result=send([bad,good],{session:{id:'a'}},()=>{errors++});
 assert.deepEqual(bad.closed,[1011]);assert.equal(good.sent.length,1);
 assert.equal(result.transportErrors,1);assert.equal(errors,1);assert.equal(result.delivered,1);
});
test('socket closes during serialization: never send to a closed peer',()=>{
 const closed=socket('audience'),ready=socket('audience');
 const result=deliverLiveSnapshot([closed,ready],{session:{id:'a'}},d=>{closed.readyState=3;return audience(d)},s=>s.view==='owner',shouldDropSlowSocket);
 assert.equal(result.delivered,1);assert.equal(closed.sent.length,0);
});
test('no ready socket avoids serialization entirely',()=>{
 const closed=socket('owner');closed.readyState=3;
 assert.deepEqual(send([closed],{session:{id:'a'}}),{serialized:0,delivered:0,droppedSlow:0,transportErrors:0});
});
test('public serialization errors fail closed before any owner-only payload is delivered',()=>{
 const owner=socket('owner'),guest=socket('audience');
 assert.throws(()=>deliverLiveSnapshot([owner,guest],{session:{id:'a'}},()=>{throw Error('projection failed')},s=>s.view==='owner'),/projection failed/);
 assert.equal(owner.sent.length,0);assert.equal(guest.sent.length,0);
});
