import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readFile,writeFile,symlink,stat,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
import {
 ASSET_DELETE_WITH_CLEANUP_SQL,ASSET_ERASURE_CLAIM_SQL,ASSET_ERASURE_ACK_SQL,
 ASSET_ERASURE_RETRY_SQL,validAssetPathIds,erasePrivateAsset,drainAssetErasureJobs
} from '../src/asset-erasure.ts';

const sid='12345678-1234-4123-8123-123456789abc';
const aid='87654321-9876-4987-8987-987654321abc';
const setup=async()=>{const root=await mkdtemp(path.join(tmpdir(),'q-erasure-'));await mkdir(path.join(root,sid));return root};

test('SQL: atomic metadata erasure and durable per-file enqueue',()=>{
 assert.match(ASSET_DELETE_WITH_CLEANUP_SQL,/WITH deleted AS/);
 assert.match(ASSET_DELETE_WITH_CLEANUP_SQL,/DELETE FROM session_assets WHERE id=\$1 AND session_id=\$2/);
 assert.match(ASSET_DELETE_WITH_CLEANUP_SQL,/INSERT INTO session_asset_file_cleanup_jobs/);
 assert.match(ASSET_DELETE_WITH_CLEANUP_SQL,/SELECT session_id,id FROM deleted/);
 assert.match(ASSET_DELETE_WITH_CLEANUP_SQL,/ON CONFLICT \(session_id,asset_id\)/);
 assert.match(ASSET_DELETE_WITH_CLEANUP_SQL,/RETURNING session_id,asset_id/);
 assert.doesNotMatch(ASSET_DELETE_WITH_CLEANUP_SQL,/TRUNCATE/);
});
test('SQL: claim is bounded, replica-safe and due-time scoped',()=>{
 for(const fragment of [/FOR UPDATE SKIP LOCKED/,/LIMIT 50/,/next_attempt_at<=now\(\)/,/attempts=attempts\+1/,/claimed_until < now\(\)/,/RETURNING session_id,asset_id,claimed_until/])assert.match(ASSET_ERASURE_CLAIM_SQL,fragment);
});
test('SQL: completion and retry are both fenced by lease and asset identity',()=>{
 for(const query of [ASSET_ERASURE_ACK_SQL,ASSET_ERASURE_RETRY_SQL]) {
  for(const fragment of [/session_id=\$1/,/asset_id=\$2/,/claimed_until=\$3/])assert.match(query,fragment);
 }
 assert.match(ASSET_ERASURE_RETRY_SQL,/next_attempt_at/);
 assert.match(ASSET_ERASURE_RETRY_SQL,/LEAST\(3600/);
 assert.match(ASSET_ERASURE_RETRY_SQL,/last_error=\$4/);
});
test('valid canonical UUIDs for independent session and file keys',()=>{
 assert.ok(validAssetPathIds(sid,aid));assert.ok(validAssetPathIds(randomUUID(),randomUUID()));
});
for(const bad of ['', '.', '..', '../etc/passwd', '/tmp', 'A'.repeat(36),sid.toUpperCase(),sid.replaceAll('-',''),sid+'/',sid+'\0', '12345678-1234-1234-1234-123456789ab/']){
 test(`reject invalid file and session key ${JSON.stringify(bad)}`,()=>{
  assert.equal(validAssetPathIds(sid,bad),false);
  assert.equal(validAssetPathIds(bad,aid),false);
 });
}
test('deletes only the requested file, preserves unrelated assets and sessions',async()=>{
 const root=await setup();try {
  await writeFile(path.join(root,sid,aid),'private');
  const other=randomUUID();await writeFile(path.join(root,sid,other),'keep');
  await erasePrivateAsset(root,sid,aid);
  await assert.rejects(stat(path.join(root,sid,aid)),{code:'ENOENT'});
  assert.equal(await readFile(path.join(root,sid,other),'utf8'),'keep');
 } finally {await rm(root,{recursive:true,force:true})}
});
test('missing file is idempotently erased',async()=>{
 const root=await setup();try {await erasePrivateAsset(root,sid,aid);await erasePrivateAsset(root,sid,aid)}
 finally {await rm(root,{recursive:true,force:true})}
});
test('missing session folder is idempotently erased',async()=>{
 const root=await setup();try {await rm(path.join(root,sid),{recursive:true});await erasePrivateAsset(root,sid,aid)}
 finally {await rm(root,{recursive:true,force:true})}
});
test('refuses symlinked session folder, leaving outside content intact',async()=>{
 const root=await setup(),outside=await mkdtemp(path.join(tmpdir(),'q-erasure-outside-'));
 try {
  await rm(path.join(root,sid),{recursive:true});await writeFile(path.join(outside,aid),'secret');
  await symlink(outside,path.join(root,sid));
  await assert.rejects(erasePrivateAsset(root,sid,aid),/unsafe_asset_folder/);
  assert.equal(await readFile(path.join(outside,aid),'utf8'),'secret');
 }finally{await rm(root,{recursive:true,force:true});await rm(outside,{recursive:true,force:true})}
});
test('a symlink file is unlinked but outside target is never erased',async()=>{
 const root=await setup(),outside=await mkdtemp(path.join(tmpdir(),'q-erasure-outside-'));
 try{
  const target=path.join(outside,'target');await writeFile(target,'secret');
  await symlink(target,path.join(root,sid,aid));await erasePrivateAsset(root,sid,aid);
  await assert.rejects(stat(path.join(root,sid,aid)),{code:'ENOENT'});
  assert.equal(await readFile(target,'utf8'),'secret');
 }finally{await rm(root,{recursive:true,force:true});await rm(outside,{recursive:true,force:true})}
});
test('directory in place of asset is a retryable failure, not recursive erasure',async()=>{
 const root=await setup();try{
  await mkdir(path.join(root,sid,aid));
  await assert.rejects(erasePrivateAsset(root,sid,aid));
  assert.ok((await stat(path.join(root,sid,aid))).isDirectory());
 }finally{await rm(root,{recursive:true,force:true})}
});
test('worker drains a claimed file, acknowledges exact lease and returns counts',async()=>{
 const root=await setup();const calls:{sql:string;args?:unknown[]}[]=[];
 try{
  await writeFile(path.join(root,sid,aid),'private');
  const claim={session_id:sid,asset_id:aid,claimed_until:new Date('2026-11-01T00:00:00Z')};
  const db={async query(sql:string,args?:unknown[]){calls.push({sql,args});if(sql===ASSET_ERASURE_CLAIM_SQL)return {rows:[claim]};return {rows:[],rowCount:1}}};
  assert.deepEqual(await drainAssetErasureJobs(db,root),{claimed:1,erased:1,retryQueued:0});
  assert.deepEqual(calls.map(x=>x.sql),[ASSET_ERASURE_CLAIM_SQL,ASSET_ERASURE_ACK_SQL]);
  assert.deepEqual(calls[1].args,[sid,aid,claim.claimed_until]);
  await assert.rejects(stat(path.join(root,sid,aid)),{code:'ENOENT'});
 }finally{await rm(root,{recursive:true,force:true})}
});
test('worker schedules retry on unsafe file and never logs filesystem path',async()=>{
 const root=await setup();const calls:{sql:string;args?:unknown[]}[]=[];
 try{
  await mkdir(path.join(root,sid,aid));
  const claim={session_id:sid,asset_id:aid,claimed_until:new Date()};
  const db={async query(sql:string,args?:unknown[]){calls.push({sql,args});if(sql===ASSET_ERASURE_CLAIM_SQL)return {rows:[claim]};return {rows:[],rowCount:1}}};
  assert.deepEqual(await drainAssetErasureJobs(db,root),{claimed:1,erased:0,retryQueued:1});
  assert.equal(calls[1].sql,ASSET_ERASURE_RETRY_SQL);
  assert.ok(['EISDIR','EPERM','cleanup_failed'].includes(String(calls[1].args?.[3])));
  assert.ok(!JSON.stringify(calls[1].args).includes(root));
 } finally {await rm(root,{recursive:true,force:true})}
});
test('worker does not claim success if a lease has been superseded',async()=>{
 const root=await setup();try{
  const db={async query(sql:string){if(sql===ASSET_ERASURE_CLAIM_SQL)return {rows:[{session_id:sid,asset_id:aid,claimed_until:new Date()}]};return {rows:[],rowCount:0}}};
  assert.deepEqual(await drainAssetErasureJobs(db,root),{claimed:1,erased:0,retryQueued:0});
 }finally{await rm(root,{recursive:true,force:true})}
});
test('empty work queue is no-op',async()=>{
 const db={async query(){return {rows:[]}}};
 assert.deepEqual(await drainAssetErasureJobs(db,'/irrelevant'),{claimed:0,erased:0,retryQueued:0});
});
test('database claim failure remains observable to caller',async()=>{
 const db={async query(){throw new Error('postgres unavailable')}};
 await assert.rejects(drainAssetErasureJobs(db,'/irrelevant'),/postgres unavailable/);
});
test('database ack failure does not silently discard durable job',async()=>{
 const root=await setup();const calls:string[]=[];
 try{
  const db={async query(sql:string){calls.push(sql);if(sql===ASSET_ERASURE_CLAIM_SQL)return {rows:[{session_id:sid,asset_id:aid,claimed_until:new Date()}]};if(sql===ASSET_ERASURE_ACK_SQL)throw new Error('postgres unavailable');return {rows:[],rowCount:1}}};
  assert.deepEqual(await drainAssetErasureJobs(db,root),{claimed:1,erased:0,retryQueued:1});
  assert.deepEqual(calls,[ASSET_ERASURE_CLAIM_SQL,ASSET_ERASURE_ACK_SQL,ASSET_ERASURE_RETRY_SQL]);
 }finally{await rm(root,{recursive:true,force:true})}
});
