import test from 'node:test';
import assert from 'node:assert/strict';
import {SESSION_CHANNEL,validSessionNotification,startSessionBus} from '../src/session-bus.ts';
test('notification channel is fixed and safe',()=>{assert.equal(SESSION_CHANNEL,'quorivio_session_update');});
test('only canonical UUID session identifiers accepted',()=>{
 assert.equal(validSessionNotification('7c151c08-80f5-4ed4-8a98-3e676537224c'),true);
 for(const bad of ['',null,42,'foo','7c151c08-80f5-4ed4-8a98-3e676537224c;DROP TABLE sessions','../../../etc/passwd'])assert.equal(validSessionNotification(bad),false);
});

test('listener refreshes local subscriptions after LISTEN and again after reconnect',async()=>{
 const events:Record<string,Function[]>={};let ready=0, connects=0, subscribed=0;
 const connect=async()=>{connects++;return {
  on(name:string,fn:Function){(events[name]??=[]).push(fn)},
  async query(sql:string){assert.equal(sql,`LISTEN ${SESSION_CHANNEL}`);subscribed++},
  async end(){}
 }};
 const stop=startSessionBus(connect,async()=>{},()=>{},async()=>{ready++});
 for(let i=0;i<30&&ready<1;i++)await new Promise(r=>setTimeout(r,5));
 assert.equal(ready,1);assert.equal(subscribed,1);
 events.end[0]();
 for(let i=0;i<150&&ready<2;i++)await new Promise(r=>setTimeout(r,10));
 assert.equal(connects,2);assert.equal(ready,2);
 await stop();
});


test('failed reconnect resynchronization retries instead of silently leaving stale subscribers',async()=>{
 let connects=0,ready=0,closed=0;
 const connect=async()=>{connects++;return {
  on(_name:string,_fn:Function){},
  async query(_sql:string){},
  async end(){closed++}
 }};
 const stop=startSessionBus(connect,async()=>{},()=>{},async()=>{ready++;if(ready===1)throw Error('database snapshot failed')});
 for(let i=0;i<160&&ready<2;i++)await new Promise(r=>setTimeout(r,10));
 assert.equal(ready,2);assert.equal(connects,2);assert.ok(closed>=1);
 await stop();
});

test('LISTEN subscription failure reconnects and replays local snapshots',async()=>{
 let connects=0,ready=0,closed=0;
 const connect=async()=>{connects++;return {
  on(_name:string,_fn:Function){},
  async query(_sql:string){if(connects===1)throw Error('LISTEN failed')},
  async end(){closed++}
 }};
 const stop=startSessionBus(connect,async()=>{},()=>{},async()=>{ready++});
 for(let i=0;i<160&&ready<1;i++)await new Promise(r=>setTimeout(r,10));
 assert.equal(connects,2);assert.equal(ready,1);assert.ok(closed>=1);
 await stop();
});


test('notifications from a disconnected listener cannot update current session state',async()=>{
 const listeners:Array<Record<string,Function[]>>=[];const seen:string[]=[];let ready=0;
 const connect=async()=>{const events:Record<string,Function[]>={};listeners.push(events);return {
  on(name:string,fn:Function){(events[name]??=[]).push(fn)},
  async query(_sql:string){},async end(){}
 }};
 const stop=startSessionBus(connect,async sid=>{seen.push(sid)},()=>{},async()=>{ready++});
 for(let i=0;i<30&&ready<1;i++)await new Promise(r=>setTimeout(r,5));
 const id='7c151c08-80f5-4ed4-8a98-3e676537224c';
 listeners[0].end[0]();
 for(let i=0;i<160&&ready<2;i++)await new Promise(r=>setTimeout(r,10));
 assert.equal(ready,2);
 listeners[0].notification[0]({channel:SESSION_CHANNEL,payload:id});
 listeners[1].notification[0]({channel:SESSION_CHANNEL,payload:id});
 await new Promise(r=>setImmediate(r));
 assert.deepEqual(seen,[id]);await stop();
 listeners[1].notification[0]({channel:SESSION_CHANNEL,payload:id});
 assert.deepEqual(seen,[id]);
});


test('a rejected notification refresh triggers reconnection and resnapshot',async()=>{
 const listeners:Array<Record<string,Function[]>>=[];let ready=0,closed=0;
 const connect=async()=>{const events:Record<string,Function[]>={};listeners.push(events);return {
  on(name:string,fn:Function){(events[name]??=[]).push(fn)},
  async query(_sql:string){},async end(){closed++}
 }};
 const stop=startSessionBus(connect,async()=>{throw Error('transient database failure')},()=>{},async()=>{ready++});
 for(let i=0;i<30&&ready<1;i++)await new Promise(r=>setTimeout(r,5));
 listeners[0].notification[0]({channel:SESSION_CHANNEL,payload:'7c151c08-80f5-4ed4-8a98-3e676537224c'});
 for(let i=0;i<160&&ready<2;i++)await new Promise(r=>setTimeout(r,10));
 assert.equal(ready,2);assert.equal(listeners.length,2);assert.ok(closed>=1);await stop();
});
