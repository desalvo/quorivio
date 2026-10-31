#!/usr/bin/env node
/** End-to-end federated identity self-service acceptance against a real API and
 * disposable PostgreSQL 18. No external provider and no production credentials.
 */
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import bcrypt from 'bcryptjs';
import pg from 'pg';

const url=new URL(process.env.DATABASE_URL||'postgres://invalid');
assert.equal(process.env.QUORIVIO_CI_FEDERATED_IDENTITIES_TEST,'1','explicit disposable CI opt-in required');
assert.match(process.env.GITHUB_RUN_ID||'',/^\d+$/,'requires GitHub disposable CI');
assert.ok(['localhost','127.0.0.1'].includes(url.hostname)&&url.pathname==='/quorivio','disposable loopback database only');
const base='http://127.0.0.1:8080';
const db=new pg.Client({connectionString:url.toString()});
const first=randomUUID(),other=randomUUID(),password='ci-only-federated-password-123';
const subject='cycle61-'+randomUUID();
let created=false;
async function api(path,method='GET',body,token=''){
 const r=await fetch(base+path,{method,redirect:'manual',headers:{'content-type':'application/json',...(token?{'cookie':token}:{})},body:body===undefined?undefined:JSON.stringify(body)});
 return {status:r.status,json:await r.json(),cookie:r.headers.get('set-cookie')||'',cache:r.headers.get('cache-control')||''};
}
try {
 await db.connect();
 const org=await db.query('SELECT id FROM organizations LIMIT 1');
 assert.equal(org.rowCount,1,'CI bootstrap must create an organization');
 const passHash=await bcrypt.hash(password,8);
 await db.query(`INSERT INTO users(id,organization_id,email,password_hash,role,approved,must_change_password)
 VALUES($1,$3,$4,$5,'user',true,false),($2,$3,$6,$5,'user',true,false)`,
 [first,other,org.rows[0].id,`ci-first-${first}@example.invalid`,passHash,`ci-other-${other}@example.invalid`]);
 created=true;
 await db.query(`INSERT INTO oidc_identities(provider,subject,user_id) VALUES('google',$1,$2),('github',$3,$4)`,[subject,first,'cycle61-'+randomUUID(),other]);
 const logged=await api('/api/auth/login','POST',{email:`ci-first-${first}@example.invalid`,password});
 assert.equal(logged.status,200,'independent account must authenticate');
 const session=logged.cookie.split(';',1)[0];assert.match(session,/^q_auth=/,'signed auth cookie missing');
 let listed=await api('/api/auth/identities','GET',undefined,session);
 assert.equal(listed.status,200);assert.match(listed.cache,/no-store/);
 assert.deepEqual(listed.json.identities.map(x=>x.provider),['google']);
 assert.ok(!JSON.stringify(listed.json).includes(subject),'subject identifier leaked');
 assert.ok(!JSON.stringify(listed.json).includes(other),'other account leaked');
 assert.equal((await api('/api/auth/identities','GET')).status,401,'anonymous listing not rejected');
 assert.equal((await api('/api/auth/identities/unlink','POST',{provider:'google',password})).status,401,'anonymous unlink not rejected');
 assert.equal((await api('/api/auth/identities/unlink','POST',{provider:'google',password:'wrong'},session)).status,403,'invalid password must fail');
 assert.equal((await api('/api/auth/identities/unlink','POST',{provider:'GITHUB',password},session)).status,400,'invalid provider must fail');
 assert.equal((await api('/api/auth/identities/unlink','POST',{provider:'github',password},session)).status,404,'other user identity must remain inaccessible');
 let result=await api('/api/auth/identities/unlink','POST',{provider:'google',password},session);
 assert.equal(result.status,200,'correct password must unlink');assert.equal(result.json.ok,true);
 assert.match(result.cache,/no-store/);
 assert.equal((await api('/api/auth/identities/unlink','POST',{provider:'google',password},session)).status,404,'replayed unlink must not succeed');
 listed=await api('/api/auth/identities','GET',undefined,session);
 assert.deepEqual(listed.json.identities,[],'removed identity still listed');
 assert.equal((await db.query('SELECT provider FROM oidc_identities WHERE user_id=$1',[other])).rowCount,1,'foreign identity deleted');
 // Simulate credential rotation following an authenticated request; the old
 // session may no longer enumerate or change provider links.
 await db.query('UPDATE users SET password_changed_at=now() WHERE id=$1',[first]);
 assert.equal((await api('/api/auth/identities','GET',undefined,session)).status,401,'password rotation must revoke listing');
 assert.equal((await api('/api/auth/identities/unlink','POST',{provider:'github',password},session)).status,401,'password rotation must revoke unlink');
 console.log('PASS disposable PostgreSQL API SSO management: user isolation, private listing, password confirmation, unlink replay and revocation');
} catch(error){
 console.error('FAIL disposable PostgreSQL SSO management',error instanceof assert.AssertionError?error.message:'database or API acceptance error');
 process.exitCode=1;
} finally {
 if(created)await db.query('DELETE FROM users WHERE id=$1 OR id=$2',[first,other]).catch(()=>{process.exitCode=1});
 await db.end().catch(()=>{});
}
