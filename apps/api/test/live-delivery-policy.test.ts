import test from 'node:test';
import assert from 'node:assert/strict';
import {MAX_LIVE_SOCKET_BUFFER_BYTES,shouldDropSlowSocket} from '../src/live-delivery-policy.ts';
test('socket delivery permits bounded pending snapshots',()=>{
 assert.equal(shouldDropSlowSocket(0,1024),false);
 assert.equal(shouldDropSlowSocket(MAX_LIVE_SOCKET_BUFFER_BYTES-10,10),false);
 assert.equal(shouldDropSlowSocket(MAX_LIVE_SOCKET_BUFFER_BYTES-10,11),true);
});
test('socket delivery fails closed for invalid accounting',()=>{
 for(const n of [-1,Infinity,NaN,1.2])assert.equal(shouldDropSlowSocket(n,10),true);
 assert.equal(shouldDropSlowSocket(0,-1),true);
});
