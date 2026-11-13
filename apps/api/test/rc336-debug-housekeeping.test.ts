import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,stat,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {debugBundlePath,purgeDebugSubmissions} from '../src/debug-submissions.ts';

const ID='123e4567-e89b-42d3-a456-426614174000';

test('expired consented debug bundles are purged without extra PostgreSQL bind parameters',async()=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'quorivio-rc336-purge-'));
 const statements:{sql:string;params?:unknown[]}[]=[];
 let released=false;
 const cx={
  async query(sql:string,params?:unknown[]){
   statements.push({sql,params});
   if(sql.startsWith('SELECT id FROM debug_submissions')){
    assert.equal(params,undefined,'a query without $1 must receive no bind parameters');
    return {rows:[{id:ID}]};
   }
   if(sql.startsWith('DELETE FROM debug_submissions')){
    assert.deepEqual(params,[ID]);
   }
   return {rows:[]};
  },
  release(){released=true}
 };
 try{
  await mkdir(path.join(root,'debug-submissions'));
  const archive=debugBundlePath(root,ID);
  await writeFile(archive,'no personally identifying data');
  const deleted=await purgeDebugSubmissions({connect:async()=>cx} as any,root,30);
  assert.equal(deleted,1);
  assert.equal(released,true);
  assert.deepEqual(statements.map(s=>s.sql==='BEGIN'||s.sql==='COMMIT'?s.sql:s.sql.split(' ')[0]),['BEGIN','SELECT','DELETE','COMMIT']);
  await assert.rejects(stat(archive),{code:'ENOENT'});
 }finally{await rm(root,{recursive:true,force:true})}
});

test('failed archive deletion rolls back database mutation and releases the connection',async()=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'quorivio-rc336-rollback-'));
 const statements:string[]=[];
 let released=false;
 const cx={
  async query(sql:string,params?:unknown[]){
   statements.push(sql);
   if(sql.startsWith('SELECT id FROM debug_submissions')){
    assert.equal(params,undefined);
    return {rows:[{id:ID}]};
   }
   return {rows:[]};
  },
  release(){released=true}
 };
 try{
  // Deliberately create a directory where a .quo archive should be.
  await mkdir(path.dirname(debugBundlePath(root,ID)),{recursive:true});
  await mkdir(debugBundlePath(root,ID));
  await assert.rejects(purgeDebugSubmissions({connect:async()=>cx} as any,root,30));
  assert.ok(statements.includes('ROLLBACK'));
  assert.ok(!statements.some(sql=>sql.startsWith('DELETE FROM debug_submissions')));
  assert.ok(!statements.includes('COMMIT'));
  assert.equal(released,true);
 }finally{await rm(root,{recursive:true,force:true})}
});

test('expired metadata is removable even if its physical .quo file was already deleted',async()=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'quorivio-rc336-missing-'));
 const queries:string[]=[];
 const cx={async query(sql:string){queries.push(sql);return {rows:sql.startsWith('SELECT id')?[{id:ID}]:[]}},release(){}};
 try{
  assert.equal(await purgeDebugSubmissions({connect:async()=>cx} as any,root,30),1);
  assert.ok(queries.includes('COMMIT'));
 }finally{await rm(root,{recursive:true,force:true})}
});
