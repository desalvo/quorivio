import {test} from 'node:test';
import assert from 'node:assert/strict';
import {BOOTSTRAP_LOCK_KEYS,withBootstrapLock} from '../src/bootstrap-lock.ts';

function fakePool(events:string[], opts:{failAcquire?:boolean,failAction?:boolean,failUnlock?:boolean}={}){
  let released=false;
  const client={
    async query(sql:string,params?:unknown[]){
      if(sql.includes('pg_advisory_lock(')){
        assert.deepEqual(params, [...BOOTSTRAP_LOCK_KEYS]);
        if(opts.failAcquire) throw Error('db_lock_timeout');
        events.push('lock');
      } else if(sql.includes('pg_advisory_unlock(')){
        events.push('unlock');
        if(opts.failUnlock)throw Error('db_disconnected');
        return {rows:[{released:true}]};
      } else events.push(sql);
      return {rows:[]};
    },
    release(destroy?:boolean){assert.equal(released,false); released=true;events.push(destroy?'release-destroy':'release');}
  };
  return {async connect(){events.push('connect');return client;}} as any;
}

test('serial migration uses one connected session and releases after work',async()=>{
  const events:string[]=[];
  await withBootstrapLock(fakePool(events),async client=>{
    await client.query('schema.sql');
    await client.query('BEGIN');
    await client.query('first-account-bootstrap');
    await client.query('COMMIT');
  });
  assert.deepEqual(events,["connect","SET lock_timeout = '120s'","lock","SET lock_timeout = DEFAULT","schema.sql","BEGIN","first-account-bootstrap","COMMIT","unlock","release"]);
});

test('migration failure releases advisory lock and original error',async()=>{
  const events:string[]=[];
  await assert.rejects(withBootstrapLock(fakePool(events),async()=>{throw Error('schema_rejected');}),/schema_rejected/);
  assert.deepEqual(events.slice(-2),['unlock','release']);
});

test('lock acquisition failure does not unlock somebody else’s lock',async()=>{
  const events:string[]=[];
  await assert.rejects(withBootstrapLock(fakePool(events,{failAcquire:true}),async()=>{throw Error('must_not_run');}),/db_lock_timeout/);
  assert.equal(events.includes('unlock'),false);
  assert.equal(events.at(-1),'release');
});

test('uncertain unlock destroys the session, never re-pools a locked connection',async()=>{
  const events:string[]=[];
  await withBootstrapLock(fakePool(events,{failUnlock:true}),async()=>{});
  assert.deepEqual(events.slice(-2),['unlock','release-destroy']);
});

// Simulates PostgreSQL session lock arbitration between two API replicas.
test('two replica bootstrap operations never overlap even if started together',async()=>{
  let held=false;let unblock:()=>void=()=>{};
  const signals:string[]=[];
  const pool={async connect(){return {
    async query(sql:string){
      if(sql.includes('pg_advisory_lock(')){
        while(held)await new Promise<void>(resolve=>{unblock=resolve});
        held=true;signals.push('acquired');
      }else if(sql.includes('pg_advisory_unlock(')){
        held=false;signals.push('released');unblock();return {rows:[{released:true}]};
      }return {rows:[]};
    },release(){},
  };}} as any;
  let active=0;let maximum=0;
  await Promise.all([1,2].map(id=>withBootstrapLock(pool,async()=>{
    active++;maximum=Math.max(maximum,active);signals.push('enter'+id);
    await new Promise(resolve=>setImmediate(resolve));
    active--;signals.push('exit'+id);
  })));
  assert.equal(maximum,1);
  assert.deepEqual(signals.filter(x=>x==='acquired'||x==='released'),['acquired','released','acquired','released']);
});
