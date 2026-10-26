#!/usr/bin/env node
/** Real PostgreSQL transactional acceptance of retention and durable media cleanup.
 * Disposable CI only; transaction is always rolled back. No credentials logged.
 */
import assert from 'node:assert/strict';
import {randomUUID,randomBytes} from 'node:crypto';
import {mkdtemp,mkdir,writeFile,readFile,stat,rm} from 'node:fs/promises';
import path from 'node:path';
import {tmpdir} from 'node:os';
import pg from 'pg';
import {SESSION_RETENTION_PURGE_SQL,SESSION_DELETE_WITH_CLEANUP_SQL,SESSION_CLEANUP_CLAIM_SQL,SESSION_RETENTION_DEFAULT_SQL} from '../apps/api/dist/session-retention.js';
import {ASSET_DELETE_WITH_CLEANUP_SQL,ASSET_ERASURE_CLAIM_SQL,PROFILE_ERASURE_ENQUEUE_SQL,drainAssetErasureJobs,drainProfileErasureJobs} from '../apps/api/dist/asset-erasure.js';
if (!process.env.DATABASE_URL || process.env.QUORIVIO_CI_RETENTION_TEST !== '1') throw Error('Disposable CI database and explicit opt-in required');
const client=new pg.Client({connectionString:process.env.DATABASE_URL});
await client.connect();
const id=()=>randomUUID();
const insert=async (name,status,expiry,closed,days)=>{
 const sid=id();
 await client.query(`INSERT INTO sessions(id,organization_id,owner_id,title,join_code,join_secret,status,expires_at,closed_at,retention_days)
 SELECT $1,organization_id,id,$2,$3,$4,$5,now()+($6::int * interval '1 day'),
 CASE WHEN $7::int IS NULL THEN NULL ELSE now()+($7::int * interval '1 day') END,$8
 FROM users WHERE is_primary_admin=true LIMIT 1`,[sid,name,randomBytes(5).toString('hex'),randomBytes(20).toString('hex'),status,expiry,closed,days]);
 return sid;
};
const fixtureRoot=await mkdtemp(path.join(tmpdir(),'quorivio-privacy-ci-'));
try {
 await client.query('BEGIN');
 const admin=(await client.query('SELECT id FROM users WHERE is_primary_admin=true LIMIT 1')).rows[0]?.id;
 assert.ok(admin,'CI bootstrap administrator is required');
 const due=await insert('CI retention due','closed',-100,-5,1);
 const held=await insert('CI retention held','closed',-100,-5,60);
 const expired=await insert('CI retention expired','active',-10,null,1);
 const live=await insert('CI retention live','active',10,null,1);
 const legacy=await insert('CI retention legacy','closed',10,null,1);
 const manual=await insert('CI retention manual','draft',10,null,1);
 const wrongOwner=await client.query(SESSION_DELETE_WITH_CLEANUP_SQL,[manual,id()]);
 assert.equal(wrongOwner.rowCount,0,'non-owner must not erase or queue');
 const manualDelete=await client.query(SESSION_DELETE_WITH_CLEANUP_SQL,[manual,admin]);
 assert.equal(manualDelete.rowCount,1,'owner deletion must enqueue media');
 const purge=await client.query(SESSION_RETENTION_PURGE_SQL);
 const ids=new Set(purge.rows.map(row=>row.id));
 assert.ok(ids.has(due) && ids.has(expired),'due and expired sessions must purge');
 for(const untouched of [held,live,legacy])assert.ok(!ids.has(untouched),'session retained too briefly');
 const queued=await client.query('SELECT session_id FROM session_asset_cleanup_jobs WHERE session_id=ANY($1::uuid[])',[[due,expired,manual]]);
 assert.equal(queued.rowCount,3,'every deletion must have durable cleanup work');
 const claims=await client.query(SESSION_CLEANUP_CLAIM_SQL);
 assert.ok(claims.rows.every(row=>row.claimed_until instanceof Date),'session leases must decode as JavaScript Dates');
 // Validate the third (session-directory) worker's exact lease ACK using the
 // same timestamp returned by node-postgres, not a server-side expression.
 const dueClaim=claims.rows.find(row=>row.session_id===due);
 assert.ok(dueClaim,'due session cleanup must be claimable');
 const staleAck=await client.query('DELETE FROM session_asset_cleanup_jobs WHERE session_id=$1 AND claimed_until=$2',[due,new Date(dueClaim.claimed_until.getTime()+1)]);
 assert.equal(staleAck.rowCount,0,'superseded lease must never ACK another worker');
 const claimedAck=await client.query('DELETE FROM session_asset_cleanup_jobs WHERE session_id=$1 AND claimed_until=$2',[due,dueClaim.claimed_until]);
 assert.equal(claimedAck.rowCount,1,'session cleanup ACK must match its Node Date lease');
 assert.ok(claims.rows.some(row=>row.session_id===manual),'manual erasure must be claimable');
 const twice=await client.query(SESSION_CLEANUP_CLAIM_SQL);
 assert.ok(!twice.rows.some(row=>row.session_id===manual),'leased job must not be claimed twice');
 // Individual asset metadata and file must be erased together with a durable
 // retry, and deleting an unrelated asset/session cannot enqueue any work.
 const asset=id(),otherAsset=id();
 await client.query(`INSERT INTO session_assets(id,session_id,uploaded_by,mime_type,byte_size,sha256)
 VALUES($1,$2,$3,'image/png',7,$4)`,[asset,held,admin,'0'.repeat(64)]);
 const unrelated=await client.query(ASSET_DELETE_WITH_CLEANUP_SQL,[otherAsset,held]);
 assert.equal(unrelated.rowCount,0,'unknown asset must not enqueue erasure');
 const wrongParent=await client.query(ASSET_DELETE_WITH_CLEANUP_SQL,[asset,live]);
 assert.equal(wrongParent.rowCount,0,'cross-session deletion must not enqueue erasure');
 const assetDeleted=await client.query(ASSET_DELETE_WITH_CLEANUP_SQL,[asset,held]);
 assert.equal(assetDeleted.rowCount,1,'correct parent must atomically queue file erasure');
 const assetJob=await client.query('SELECT session_id,asset_id,attempts FROM session_asset_file_cleanup_jobs WHERE asset_id=$1',[asset]);
 assert.equal(assetJob.rowCount,1);
 assert.equal(assetJob.rows[0].session_id,held);
 assert.equal(Number(assetJob.rows[0].attempts),0);
 await mkdir(path.join(fixtureRoot,held),{recursive:true});
 await writeFile(path.join(fixtureRoot,held,asset),'private');
 const otherFile=id();await writeFile(path.join(fixtureRoot,held,otherFile),'preserve');
 const assetSummary=await drainAssetErasureJobs(client,fixtureRoot);
 assert.equal(assetSummary.claimed,1,'one file outbox job must be claimed in clean CI');
 assert.equal(assetSummary.retryQueued,0,'file removal and ACK must not need a retry');
 assert.ok(assetSummary.erased>=1,'physical file worker must acknowledge after actual unlink');
 await assert.rejects(stat(path.join(fixtureRoot,held,asset)),{code:'ENOENT'});
 assert.equal(await readFile(path.join(fixtureRoot,held,otherFile),'utf8'),'preserve');
 assert.equal((await client.query('SELECT count(*)::int AS n FROM session_asset_file_cleanup_jobs WHERE asset_id=$1',[asset])).rows[0].n,0);
 // Avatar replacement and user deletion both use this profile erasure outbox.
 const photo=id();await mkdir(path.join(fixtureRoot,'profile-photos'),{recursive:true});
 await writeFile(path.join(fixtureRoot,'profile-photos',photo),'private-profile');
 await client.query(PROFILE_ERASURE_ENQUEUE_SQL,[photo]);
 const photoSummary=await drainProfileErasureJobs(client,fixtureRoot);
 assert.equal(photoSummary.claimed,1,'one avatar outbox job must be claimed in clean CI');
 assert.equal(photoSummary.retryQueued,0,'avatar removal and ACK must not need a retry');
 assert.ok(photoSummary.erased>=1);
 await assert.rejects(stat(path.join(fixtureRoot,'profile-photos',photo)),{code:'ENOENT'});
 assert.equal((await client.query('SELECT count(*)::int AS n FROM profile_photo_cleanup_jobs WHERE photo_id=$1',[photo])).rows[0].n,0);
 // Failed work is delayed with bounded backoff and can be retried on lease expiry.
 const failAsset=id();
 await client.query(ASSET_DELETE_WITH_CLEANUP_SQL,[otherAsset,held]); // remains a no-op
 await client.query('INSERT INTO session_asset_file_cleanup_jobs(session_id,asset_id) VALUES($1,$2)',[held,failAsset]);
 const requeued=await client.query("UPDATE session_asset_file_cleanup_jobs SET next_attempt_at=now()+interval '1 hour' WHERE session_id=$1 AND asset_id=$2 RETURNING next_attempt_at",[held,failAsset]);
 assert.equal(requeued.rowCount,1);
 const earlyClaim=await client.query(ASSET_ERASURE_CLAIM_SQL);
 assert.ok(!earlyClaim.rows.some(row=>row.asset_id===failAsset),'not-yet-due retries cannot be stolen by another replica');
 // Expired leases are reclaimable after worker crashes (without advancing the clock).
 await client.query("UPDATE session_asset_cleanup_jobs SET claimed_until=now()-interval '1 second' WHERE session_id=$1",[manual]);
 const reclaimed=await client.query(SESSION_CLEANUP_CLAIM_SQL);
 assert.ok(reclaimed.rows.some(row=>row.session_id===manual),'stale session lease must be reclaimable');
 const setting=await client.query(`SELECT ${SESSION_RETENTION_DEFAULT_SQL} AS days`);
 assert.ok(Number(setting.rows[0].days)>=1,'administrator retention default is present');
 console.log('PASS PostgreSQL retention and erasure: session and individual file outboxes, profile erasure, scoped deletes, physical filesystem deletion, queued retry/backoff, lease fencing and default');
} finally {
 await client.query('ROLLBACK').catch(()=>{});
 await client.end();
 await rm(fixtureRoot,{recursive:true,force:true});
}
