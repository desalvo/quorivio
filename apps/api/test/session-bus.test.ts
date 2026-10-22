import test from 'node:test';
import assert from 'node:assert/strict';
import {SESSION_CHANNEL,validSessionNotification} from '../src/session-bus.ts';
test('notification channel is fixed and safe',()=>{assert.equal(SESSION_CHANNEL,'quorivio_session_update');});
test('only canonical UUID session identifiers accepted',()=>{
 assert.equal(validSessionNotification('7c151c08-80f5-4ed4-8a98-3e676537224c'),true);
 for(const bad of ['',null,42,'foo','7c151c08-80f5-4ed4-8a98-3e676537224c;DROP TABLE sessions','../../../etc/passwd'])assert.equal(validSessionNotification(bad),false);
});
