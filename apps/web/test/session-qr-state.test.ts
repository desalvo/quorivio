import test from 'node:test';
import assert from 'node:assert/strict';
import {EMPTY_QR_TARGET,updateQrTarget,visibleQrTarget} from '../src/session-qr-state.ts';

test('new authoritative URL increments the image revision exactly once',()=>{
 const first=updateQrTarget(EMPTY_QR_TARGET,'owner:session:code1','https://audience.example/join/old');
 assert.equal(first.revision,1);
 const repeated=updateQrTarget(first,'owner:session:code1','https://audience.example/join/old');
 assert.strictEqual(repeated,first);
 const rotated=updateQrTarget(first,'owner:session:code1','https://audience.example/join/new');
 assert.equal(rotated.revision,2);
 assert.equal(rotated.url,'https://audience.example/join/new');
});

test('switching session code hides prior QR without awaiting a refresh',()=>{
 const first=updateQrTarget(EMPTY_QR_TARGET,'owner:session:old-code','https://audience.example/join/old');
 assert.equal(visibleQrTarget(first,'owner:session:new-code'),null);
 const second=updateQrTarget(first,'owner:session:new-code','https://audience.example/join/new');
 assert.equal(second.revision,1);
 assert.equal(second.url,'https://audience.example/join/new');
});

test('revoked public URL removes scannable pixels and cannot keep stale text',()=>{
 const first=updateQrTarget(EMPTY_QR_TARGET,'public:session','https://audience.example/join/old');
 const failed=updateQrTarget(first,'public:session',null);
 assert.equal(failed.url,'');
 assert.equal(failed.failed,true);
 assert.equal(failed.revision,2);
 assert.strictEqual(updateQrTarget(failed,'public:session',null),failed);
});

test('success after transient failure recovers without exposing old token',()=>{
 const first=updateQrTarget(EMPTY_QR_TARGET,'owner:session','https://audience.example/join/old');
 const unavailable=updateQrTarget(first,'owner:session',null);
 const next=updateQrTarget(unavailable,'owner:session','https://audience.example/join/new');
 assert.equal(next.failed,false);
 assert.equal(next.url,'https://audience.example/join/new');
 assert.equal(next.revision,3);
});
