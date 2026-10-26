import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,rm,symlink,stat} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
import {
 PROFILE_ERASURE_ENQUEUE_SQL,PROFILE_ERASURE_CLAIM_SQL,PROFILE_ERASURE_ACK_SQL,
 PROFILE_ERASURE_RETRY_SQL,erasePrivateProfilePhoto,drainProfileErasureJobs
} from '../src/asset-erasure.ts';
const photo='12345678-1234-4123-8123-123456789abc';
const setup=async()=>{const root=await mkdtemp(path.join(tmpdir(),'q-profile-erasure-'));await mkdir(path.join(root,'profile-photos'));return root};

test('profile cleanup schema commands are idempotent and lease fenced',()=>{
 assert.match(PROFILE_ERASURE_ENQUEUE_SQL,/ON CONFLICT\(photo_id\) DO UPDATE/);
 assert.match(PROFILE_ERASURE_CLAIM_SQL,/FOR UPDATE SKIP LOCKED/);
 assert.match(PROFILE_ERASURE_CLAIM_SQL,/LIMIT 50/);
 assert.match(PROFILE_ERASURE_CLAIM_SQL,/next_attempt_at<=now\(\)/);
 assert.match(PROFILE_ERASURE_CLAIM_SQL,/attempts=attempts\+1/);
 for(const query of [PROFILE_ERASURE_ACK_SQL,PROFILE_ERASURE_RETRY_SQL]){
  assert.match(query,/photo_id=\$1/);assert.match(query,/claimed_until=\$2/);
 }
 assert.match(PROFILE_ERASURE_RETRY_SQL,/LEAST\(3600/);
});
test('unlink only the old photo while keeping current photo',async()=>{
 const root=await setup();try{
  const other=randomUUID();await writeFile(path.join(root,'profile-photos',photo),'old');
  await writeFile(path.join(root,'profile-photos',other),'current');
  await erasePrivateProfilePhoto(root,photo);
  await assert.rejects(stat(path.join(root,'profile-photos',photo)),{code:'ENOENT'});
  assert.equal(await readFile(path.join(root,'profile-photos',other),'utf8'),'current');
 }finally{await rm(root,{recursive:true,force:true})}
});
test('missing profile photo is safe to retry',async()=>{
 const root=await setup();try{await erasePrivateProfilePhoto(root,photo);await erasePrivateProfilePhoto(root,photo)}
 finally{await rm(root,{recursive:true,force:true})}
});
test('missing profile folder is safe to retry',async()=>{
 const root=await setup();try{await rm(path.join(root,'profile-photos'),{recursive:true});await erasePrivateProfilePhoto(root,photo)}
 finally{await rm(root,{recursive:true,force:true})}
});
for(const value of ['', '../secrets', '/etc/passwd','a'.repeat(36),photo.toUpperCase(),photo+'/','12']){
 test('invalid photo file identifier rejects before filesystem access: '+JSON.stringify(value),async()=>{
  await assert.rejects(erasePrivateProfilePhoto('/missing-root',value),/invalid_profile_photo_id/);
 });
}
test('symlinked profile-photos folder is rejected',async()=>{
 const root=await setup(),external=await mkdtemp(path.join(tmpdir(),'q-photo-external-'));
 try{
  await rm(path.join(root,'profile-photos'),{recursive:true});
  await writeFile(path.join(external,photo),'private');
  await symlink(external,path.join(root,'profile-photos'));
  await assert.rejects(erasePrivateProfilePhoto(root,photo),/unsafe_profile_photo_folder/);
  assert.equal(await readFile(path.join(external,photo),'utf8'),'private');
 }finally{await rm(root,{recursive:true,force:true});await rm(external,{recursive:true,force:true})}
});
test('profile worker acknowledges exactly its claimed lease',async()=>{
 const root=await setup();const statements:{sql:string;args?:unknown[]}[]=[];
 try{
  await writeFile(path.join(root,'profile-photos',photo),'private');
  const token=new Date('2026-10-26T10:00:00Z');
  const db={async query(sql:string,args?:unknown[]){statements.push({sql,args});return sql===PROFILE_ERASURE_CLAIM_SQL?{rows:[{photo_id:photo,claimed_until:token}]}:{rows:[],rowCount:1}}};
  assert.deepEqual(await drainProfileErasureJobs(db,root),{claimed:1,erased:1,retryQueued:0});
  assert.deepEqual(statements.map(s=>s.sql),[PROFILE_ERASURE_CLAIM_SQL,PROFILE_ERASURE_ACK_SQL]);
  assert.deepEqual(statements[1].args,[photo,token]);
  await assert.rejects(stat(path.join(root,'profile-photos',photo)),{code:'ENOENT'});
 }finally{await rm(root,{recursive:true,force:true})}
});
test('profile worker retries file errors without persisting absolute paths',async()=>{
 const root=await setup();const statements:{sql:string;args?:unknown[]}[]=[];
 try{
  await mkdir(path.join(root,'profile-photos',photo));
  const db={async query(sql:string,args?:unknown[]){statements.push({sql,args});return sql===PROFILE_ERASURE_CLAIM_SQL?{rows:[{photo_id:photo,claimed_until:new Date()}]}:{rows:[],rowCount:1}}};
  assert.deepEqual(await drainProfileErasureJobs(db,root),{claimed:1,erased:0,retryQueued:1});
  assert.equal(statements[1].sql,PROFILE_ERASURE_RETRY_SQL);
  assert.ok(!JSON.stringify(statements[1].args).includes(root));
 }finally{await rm(root,{recursive:true,force:true})}
});
test('profile worker correctly reports superseded acknowledgement',async()=>{
 const root=await setup();try{
  const db={async query(sql:string){return sql===PROFILE_ERASURE_CLAIM_SQL?{rows:[{photo_id:photo,claimed_until:new Date()}]}:{rows:[],rowCount:0}}};
  assert.deepEqual(await drainProfileErasureJobs(db,root),{claimed:1,erased:0,retryQueued:0});
 }finally{await rm(root,{recursive:true,force:true})}
});
test('profile worker empty queue is a no-op',async()=>{
 const db={async query(){return {rows:[]}}};
 assert.deepEqual(await drainProfileErasureJobs(db,'/does-not-matter'),{claimed:0,erased:0,retryQueued:0});
});
test('profile worker claim DB exception is not swallowed',async()=>{
 const db={async query(){throw new Error('database unavailable')}};
 await assert.rejects(drainProfileErasureJobs(db,'/irrelevant'),/database unavailable/);
});
