#!/usr/bin/env node
/** Disposable PostgreSQL acceptance of one-shot OAuth state, link authorization
 * and revocation between a started flow and its cross-site callback.
 * Does NOT contact Google/GitHub/Facebook or claim real-provider acceptance.
 */
import assert from 'node:assert/strict';
import {randomUUID,randomBytes} from 'node:crypto';
import pg from 'pg';
import {FEDERATED_LINK_ELIGIBLE_SQL,FEDERATED_LINK_INSERT_SQL} from '../apps/api/dist/federated-link.js';
const url=new URL(process.env.DATABASE_URL||'postgres://invalid');
assert.equal(process.env.QUORIVIO_CI_FEDERATED_LINK_TEST,'1','must explicitly opt in');
assert.match(process.env.GITHUB_RUN_ID||'',/^\d+$/,'requires disposable CI runner');
assert.ok(['localhost','127.0.0.1'].includes(url.hostname) && url.pathname==='/quorivio', 'only disposable loopback Postgres');
const db=new pg.Client({connectionString:url.toString()});
await db.connect();
const id=randomUUID(),flowHash=randomBytes(32).toString('hex');
const issuedAt=Date.now()-3000;
const email=`ci-oauth-${id}@example.invalid`;
try {
 await db.query('BEGIN');
 const org=await db.query('SELECT id FROM organizations LIMIT 1');
 assert.equal(org.rowCount,1,'CI bootstrap organization absent');
 await db.query(`INSERT INTO users(id,organization_id,email,password_hash,role,approved,must_change_password)
 VALUES($1,$2,$3,'disabled-ci-account','user',true,false)`,[id,org.rows[0].id,email]);
 const eligible=()=>db.query(FEDERATED_LINK_ELIGIBLE_SQL,[id,issuedAt]);
 const insert=(provider,subject)=>db.query(FEDERATED_LINK_INSERT_SQL,[provider,subject,id,issuedAt]);
 assert.equal((await eligible()).rowCount,1);
 await db.query(`INSERT INTO auth_flows(state_hash,kind,provider,link_user,link_auth_issued_at_ms,expires_at)
 VALUES($1,'social','github',$2,$3,now()+interval '5 minutes')`,[flowHash,id,issuedAt]);
 let state=await db.query(`DELETE FROM auth_flows WHERE state_hash=$1 AND kind='social' AND expires_at>now() RETURNING link_user,link_auth_issued_at_ms`,[flowHash]);
 assert.equal(state.rowCount,1);
 assert.equal(state.rows[0].link_auth_issued_at_ms,String(issuedAt));
 state=await db.query(`DELETE FROM auth_flows WHERE state_hash=$1 AND kind='social' AND expires_at>now() RETURNING link_user`,[flowHash]);
 assert.equal(state.rowCount,0,'replayed callback state must be rejected');
 assert.equal((await insert('github','10001')).rowCount,1,'legitimate subject must link');
 assert.equal((await insert('github','10002')).rowCount,0,'same local user cannot link two IDs from provider');
 assert.equal((await insert('github','10001')).rowCount,0,'duplicate provider identity must not link twice');
 await db.query('UPDATE users SET auth_revoked_at=now() WHERE id=$1',[id]);
 assert.equal((await eligible()).rowCount,0,'revoked cookie must not start a link');
 assert.equal((await insert('facebook','10003')).rowCount,0,'callback must fail after admin MFA revocation');
 await db.query('UPDATE users SET auth_revoked_at=NULL,password_changed_at=now() WHERE id=$1',[id]);
 assert.equal((await eligible()).rowCount,0,'rotated password must revoke old session');
 assert.equal((await insert('facebook','10004')).rowCount,0,'callback must fail after password reset');
 await db.query('UPDATE users SET password_changed_at=NULL,approved=false WHERE id=$1',[id]);
 assert.equal((await insert('facebook','10005')).rowCount,0,'unapproved user cannot link');
 await db.query('UPDATE users SET approved=true,must_change_password=true WHERE id=$1',[id]);
 assert.equal((await insert('facebook','10006')).rowCount,0,'forced password change cannot link');
 await db.query('ROLLBACK');
 console.log('PASS disposable PostgreSQL OAuth linking: valid link, duplicate prevention, one-shot state, admin revocation, password reset and approval gates');
} catch (error) {
 await db.query('ROLLBACK').catch(()=>{});
 // Never echo provider tokens, user credentials or database connection string.
 console.error('FAIL disposable PostgreSQL OAuth linking acceptance',error instanceof assert.AssertionError?error.message:'database or acceptance error');
 process.exitCode=1;
} finally {await db.end();}
