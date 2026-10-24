import test from 'node:test';
import assert from 'node:assert/strict';
import {liveSessionActive,livePresenterAuthorized,liveParticipantAuthorized} from '../src/live-socket-policy.ts';
const now=Date.now();
const session={id:'s',owner_id:'owner',status:'active',expires_at:new Date(now+60000)};
const account={id:'delegate',role:'presenter',approved:true,must_change_password:false};
test('live session closes on expiry, closure and invalid timestamps',()=>{
 assert.equal(liveSessionActive(session,now),true);
 assert.equal(liveSessionActive({...session,status:'closed'},now),false);
 assert.equal(liveSessionActive({...session,expires_at:new Date(now-1)},now),false);
 assert.equal(liveSessionActive({...session,expires_at:'invalid'},now),false);
 assert.equal(liveSessionActive(undefined,now),false);
});
test('removed co-presenter cannot retain WebSocket access',()=>{
 assert.equal(livePresenterAuthorized(session,account,true,now-1000,now),true);
 assert.equal(livePresenterAuthorized(session,account,false,now-1000,now),false);
 assert.equal(livePresenterAuthorized(session,{...account,id:'owner'},false,now-1000,now),true);
});
test('account suspension, role changes, credential revocation fail closed',()=>{
 for(const modified of [{...account,approved:false},{...account,must_change_password:true},{...account,role:'participant'},{...account,auth_revoked_at:new Date(now-100)},{...account,password_changed_at:new Date(now-100)}])
  assert.equal(livePresenterAuthorized(session,modified,true,now-1000,now),false);
 assert.equal(livePresenterAuthorized(session,account,true,null,now),false);
 assert.equal(livePresenterAuthorized(session,undefined,true,now-1000,now),false);
});

test('removed participants cannot retain a live connection',()=>{
 assert.equal(liveParticipantAuthorized(session,'participant',true,now),true);
 assert.equal(liveParticipantAuthorized(session,'participant',false,now),false);
 assert.equal(liveParticipantAuthorized(session,null,true,now),false);
 assert.equal(liveParticipantAuthorized({...session,status:'closed'},'participant',true,now),false);
});
