/** Crash-safe erasure of individual private session assets.
 * Never discard filesystem deletion intent in a request handler: row removal
 * and durable outbox insertion are one atomic PostgreSQL statement.
 */
import {lstat,unlink} from 'node:fs/promises';
import path from 'node:path';

export const ASSET_DELETE_WITH_CLEANUP_SQL = `
WITH deleted AS (
 DELETE FROM session_assets WHERE id=$1 AND session_id=$2 RETURNING id,session_id
), queued AS (
 INSERT INTO session_asset_file_cleanup_jobs(session_id,asset_id)
 SELECT session_id,id FROM deleted
 ON CONFLICT (session_id,asset_id) DO UPDATE SET
  next_attempt_at=now(), claimed_until=NULL, last_error=NULL
 RETURNING session_id,asset_id
) SELECT asset_id AS id FROM queued`;

/** A lease is shared by replicas but scoped to each file, not its session. */
export const ASSET_ERASURE_CLAIM_SQL = `
UPDATE session_asset_file_cleanup_jobs
SET claimed_until=now()+interval '5 minutes', attempts=attempts+1
WHERE (session_id,asset_id) IN (
 SELECT session_id,asset_id FROM session_asset_file_cleanup_jobs
 WHERE (claimed_until IS NULL OR claimed_until < now())
   AND next_attempt_at<=now()
 ORDER BY next_attempt_at,queued_at LIMIT 50 FOR UPDATE SKIP LOCKED
) RETURNING session_id,asset_id,claimed_until`;

export const ASSET_ERASURE_ACK_SQL = `DELETE FROM session_asset_file_cleanup_jobs
 WHERE session_id=$1 AND asset_id=$2 AND claimed_until=$3`;
export const ASSET_ERASURE_RETRY_SQL = `UPDATE session_asset_file_cleanup_jobs
 SET claimed_until=NULL,
 next_attempt_at=now()+(LEAST(3600,30*power(2,LEAST(attempts,7))) * interval '1 second'),
 last_error=$4
 WHERE session_id=$1 AND asset_id=$2 AND claimed_until=$3`;

const CANONICAL_UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
export function validAssetPathIds(sessionId:string,assetId:string):boolean {
 return CANONICAL_UUID.test(sessionId) && CANONICAL_UUID.test(assetId);
}

/** Refuse redirected parent folders rather than following a mutable symlink. */
export async function erasePrivateAsset(root:string,sessionId:string,assetId:string):Promise<void>{
 if(!validAssetPathIds(sessionId,assetId))throw new Error('invalid_asset_identifiers');
 const folder=path.join(path.resolve(root),sessionId);
 try {
  const st=await lstat(folder);
  if(!st.isDirectory() || st.isSymbolicLink())throw new Error('unsafe_asset_folder');
 } catch(e){
  if((e as NodeJS.ErrnoException).code==='ENOENT')return;
  throw e;
 }
 try{await unlink(path.join(folder,assetId))}
 catch(e){if((e as NodeJS.ErrnoException).code!=='ENOENT')throw e}
}

export interface ErasureDb {
 query(statement:string,params?:unknown[]):Promise<{rows:Record<string,any>[];rowCount?:number|null}>;
}
export interface ErasureSummary {claimed:number;erased:number;retryQueued:number;}
export function erasureFailureCode(error:unknown):string {
 const code=(error as NodeJS.ErrnoException|undefined)?.code;
 return typeof code==='string' && /^E[A-Z0-9_]{1,20}$/.test(code)?code:'cleanup_failed';
}

/** Idempotent leased worker: no raw filenames, full paths or user content in the outbox. */
export async function drainAssetErasureJobs(db:ErasureDb,root:string):Promise<ErasureSummary>{
 const claims=await db.query(ASSET_ERASURE_CLAIM_SQL);
 const summary={claimed:claims.rows.length,erased:0,retryQueued:0};
 for(const job of claims.rows){
  const params=[job.session_id,job.asset_id,job.claimed_until];
  try{
   await erasePrivateAsset(root,job.session_id,job.asset_id);
   const ack=await db.query(ASSET_ERASURE_ACK_SQL,params);
   if(ack.rowCount===1)summary.erased++;
  }catch(e){
   // If SQL itself is unavailable, preserve the lease for recovery on expiry.
   await db.query(ASSET_ERASURE_RETRY_SQL,[...params,erasureFailureCode(e)]);
   summary.retryQueued++;
  }
 }
 return summary;
}

/** User avatars live outside session folders and need an independent outbox.
 * Never delete a previously published avatar before its DB reference is changed
 * and its erasure job has committed in the same transaction.
 */
export const PROFILE_ERASURE_ENQUEUE_SQL = `INSERT INTO profile_photo_cleanup_jobs(photo_id)
 VALUES($1) ON CONFLICT(photo_id) DO UPDATE SET
 next_attempt_at=now(),claimed_until=NULL,last_error=NULL`;
export const PROFILE_ERASURE_CLAIM_SQL = `UPDATE profile_photo_cleanup_jobs
 SET claimed_until=now()+interval '5 minutes', attempts=attempts+1
 WHERE photo_id IN (
 SELECT photo_id FROM profile_photo_cleanup_jobs
 WHERE (claimed_until IS NULL OR claimed_until<now()) AND next_attempt_at<=now()
 ORDER BY next_attempt_at,queued_at LIMIT 50 FOR UPDATE SKIP LOCKED
 ) RETURNING photo_id,claimed_until`;
export const PROFILE_ERASURE_ACK_SQL = `DELETE FROM profile_photo_cleanup_jobs WHERE photo_id=$1 AND claimed_until=$2`;
export const PROFILE_ERASURE_RETRY_SQL = `UPDATE profile_photo_cleanup_jobs
 SET claimed_until=NULL,
 next_attempt_at=now()+(LEAST(3600,30*power(2,LEAST(attempts,7))) * interval '1 second'),last_error=$3
 WHERE photo_id=$1 AND claimed_until=$2`;

export async function erasePrivateProfilePhoto(root:string,photoId:string):Promise<void>{
 if(!CANONICAL_UUID.test(photoId))throw Error('invalid_profile_photo_id');
 const folder=path.join(path.resolve(root),'profile-photos');
 try{
  const st=await lstat(folder);
  if(!st.isDirectory()||st.isSymbolicLink())throw Error('unsafe_profile_photo_folder');
 }catch(e){if((e as NodeJS.ErrnoException).code==='ENOENT')return;throw e}
 try{await unlink(path.join(folder,photoId))}
 catch(e){if((e as NodeJS.ErrnoException).code!=='ENOENT')throw e}
}
export async function drainProfileErasureJobs(db:ErasureDb,root:string):Promise<ErasureSummary>{
 const claims=await db.query(PROFILE_ERASURE_CLAIM_SQL);
 const summary={claimed:claims.rows.length,erased:0,retryQueued:0};
 for(const job of claims.rows){
  const params=[job.photo_id,job.claimed_until];
  try{
   await erasePrivateProfilePhoto(root,job.photo_id);
   if((await db.query(PROFILE_ERASURE_ACK_SQL,params)).rowCount===1)summary.erased++;
  }catch(e){
   await db.query(PROFILE_ERASURE_RETRY_SQL,[...params,erasureFailureCode(e)]);
   summary.retryQueued++;
  }
 }
 return summary;
}
