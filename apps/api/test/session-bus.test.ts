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
