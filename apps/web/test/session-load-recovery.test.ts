import test from 'node:test';
import assert from 'node:assert/strict';
import {isOwnerSessionSnapshot,normalizeOwnerSessionSnapshot,sessionFailureForStatus} from '../src/session-load-recovery.ts';

const sid='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
const snapshot={session:{id:sid,title:'Sessione già avviata',status:'active'},activities:[{id:'b',type:'slide'}],results:[],totals:[]};
test('a reopened running session is recognized independently of QR rotation',()=>{
 assert.equal(isOwnerSessionSnapshot(snapshot,sid),true);
 assert.equal(isOwnerSessionSnapshot({...snapshot,session:{...snapshot.session,join_code:'new-code'}},sid),true);
});
test('stale other-session and malformed websocket snapshots cannot replace the dashboard',()=>{
 assert.equal(isOwnerSessionSnapshot(snapshot,'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),false);
 assert.equal(isOwnerSessionSnapshot({session:snapshot.session,activities:null},sid),false);
 assert.equal(isOwnerSessionSnapshot({session:snapshot.session,activities:[null],results:[],totals:[]},sid),false);
 assert.equal(isOwnerSessionSnapshot(null,sid),false);
});
test('expired authentication reauthenticates, forbidden/deleted sessions return to list, service errors retry',()=>{
 assert.equal(sessionFailureForStatus(401),'expired');
 assert.equal(sessionFailureForStatus(403),'unavailable');
 assert.equal(sessionFailureForStatus(404),'unavailable');
 assert.equal(sessionFailureForStatus(410),'unavailable');
 for(const status of [undefined,0,408,429,500,503,504])assert.equal(sessionFailureForStatus(status),'retry');
});

test('older snapshot without statistics arrays is normalized to avoid a blank dashboard',()=>{
 const older={session:snapshot.session,activities:snapshot.activities};
 assert.equal(isOwnerSessionSnapshot(older,sid),true);
 assert.deepEqual(normalizeOwnerSessionSnapshot(older),{...older,results:[],totals:[]});
});
