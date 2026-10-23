import test from 'node:test';
import assert from 'node:assert/strict';
import {authCookieIssuedAt,presenterAuthActive} from '../src/live-auth.ts';
const t=1700000000000;
test('live cookie issuance is derived from signed expiry and refuses invalid timestamps',()=>{
 assert.equal(authCookieIssuedAt(`foo=1; q_auth=user.${t+28800000}.signature`),t);
 assert.equal(authCookieIssuedAt('q_auth=bad.notanumber.signature'),null);
 assert.equal(authCookieIssuedAt(undefined),null);
});
test('live presenter authentication revokes older sockets and denies unapproved users',()=>{
 const base={approved:true,must_change_password:false,auth_revoked_at:null,password_changed_at:null};
 assert.equal(presenterAuthActive(base,t),true);
 assert.equal(presenterAuthActive({...base,auth_revoked_at:new Date(t+1)},t),false);
 assert.equal(presenterAuthActive({...base,password_changed_at:new Date(t+1)},t),false);
 assert.equal(presenterAuthActive({...base,approved:false},t),false);
 assert.equal(presenterAuthActive({...base,must_change_password:true},t),false);
 assert.equal(presenterAuthActive(base,null),false);
});
