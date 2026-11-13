/** RC332 user-consented diagnostic archive. The .quo is generated server-side
 * from an authorized session and never contains audience votes or credentials.
 * PostgreSQL row locks coordinate physical erasure across API replicas.
 */
import type {Pool} from 'pg';
import {mkdir,readFile,writeFile,unlink,lstat,readdir} from 'node:fs/promises';
import path from 'node:path';
import {randomUUID} from 'node:crypto';

export const MAX_DEBUG_BUNDLE_BYTES=80*1024*1024;
const uuid=/^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i;
export type DebugKind='bug'|'feature';
export function validateDebugSubmission(input:unknown):{kind:DebugKind;message:string;consentDiagnostics:boolean}{
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('invalid_debug_submission');
 const b=input as Record<string,unknown>;
 if(b.kind!=='bug'&&b.kind!=='feature')throw Error('invalid_debug_kind');
 if(typeof b.message!=='string'||b.message.trim().length<10||b.message.length>2000||/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(b.message))throw Error('invalid_debug_message');
 if(b.consentSubmission!==true)throw Error('debug_submission_consent_required');
 if(typeof b.consentDiagnostics!=='boolean')throw Error('debug_diagnostic_consent_required');
 return {kind:b.kind,message:b.message.trim(),consentDiagnostics:b.consentDiagnostics};
}
export function debugBundlePath(root:string,id:string){
 if(!uuid.test(id))throw Error('invalid_debug_id');
 return path.join(root,'debug-submissions',id+'.quo');
}
export async function createDebugSubmission(db:Pool,root:string,sessionId:string,userId:string,input:unknown,bundle:Buffer,diagnostics:unknown,retentionDays:number){
 const validated=validateDebugSubmission(input);
 if(!uuid.test(sessionId)||!uuid.test(userId)||!Number.isInteger(retentionDays)||retentionDays<1||retentionDays>3650||bundle.length<22||bundle.length>MAX_DEBUG_BUNDLE_BYTES)throw Error('invalid_debug_payload');
 const id=randomUUID(),file=debugBundlePath(root,id);
 await mkdir(path.dirname(file),{recursive:true,mode:0o700});
 await writeFile(file,bundle,{flag:'wx',mode:0o600});
 try{
  await db.query("INSERT INTO debug_submissions(id,session_id,user_id,kind,message,consent_diagnostics,diagnostics,expires_at) VALUES($1,$2,$3,$4,$5,$6,$7::jsonb,now()+($8::integer*interval '1 day'))",
   [id,sessionId,userId,validated.kind,validated.message,validated.consentDiagnostics,JSON.stringify(validated.consentDiagnostics?diagnostics:null),retentionDays]);
 }catch(e){await unlink(file).catch(()=>{});throw e}
 return {id,...validated,expiresInDays:retentionDays};
}
export async function listDebugSubmissions(db:Pool){
 const r=await db.query("SELECT d.id,d.session_id,d.kind,d.message,d.consent_diagnostics,d.created_at,d.expires_at,d.email_delivery_status,u.email AS sender FROM debug_submissions d JOIN users u ON u.id=d.user_id WHERE d.expires_at>now() ORDER BY d.created_at DESC LIMIT 500");
 return r.rows;
}
export async function readDebugSubmission(db:Pool,root:string,id:string):Promise<Buffer|null>{
 if(!uuid.test(id))return null;
 const row=await db.query('SELECT 1 FROM debug_submissions WHERE id=$1 AND expires_at>now()',[id]);
 if(!row.rowCount)return null;
 const file=debugBundlePath(root,id);
 const st=await lstat(file).catch(e=>{if((e as NodeJS.ErrnoException).code==='ENOENT')return null;throw e});
 if(!st||!st.isFile()||st.isSymbolicLink()||st.size>MAX_DEBUG_BUNDLE_BYTES)throw Error('invalid_debug_archive');
 return readFile(file);
}
export async function purgeDebugSubmissions(db:Pool,root:string,retentionDays:number):Promise<number>{
 if(!Number.isInteger(retentionDays)||retentionDays<1||retentionDays>3650)throw Error('invalid_debug_retention');
 const cx=await db.connect();let deleted=0;
 try{
  await cx.query('BEGIN');
  const rows=await cx.query("SELECT id FROM debug_submissions WHERE expires_at<=now() ORDER BY expires_at LIMIT 100 FOR UPDATE SKIP LOCKED",[retentionDays]);
  for(const row of rows.rows){
   const file=debugBundlePath(root,row.id);
   try{await unlink(file)}catch(e){if((e as NodeJS.ErrnoException).code!=='ENOENT')throw e}
   await cx.query('DELETE FROM debug_submissions WHERE id=$1',[row.id]);deleted++;
  }
  await cx.query('COMMIT');
 }catch(e){await cx.query('ROLLBACK').catch(()=>{});throw e}
 finally{cx.release()}
 return deleted;
}

/** Reclaim orphaned .quo archives left by an interrupted write. No active
 * registered bundle is touched, even if its filesystem timestamps are old. */
export async function removeOrphanDebugBundles(db:Pool,root:string,retentionDays:number,now=Date.now()):Promise<number>{
 if(!Number.isInteger(retentionDays)||retentionDays<1||retentionDays>3650)throw Error('invalid_debug_retention');
 const dir=path.join(root,'debug-submissions');
 const st=await lstat(dir).catch(e=>{if((e as NodeJS.ErrnoException).code==='ENOENT')return null;throw e});
 if(!st)return 0;
 if(!st.isDirectory()||st.isSymbolicLink())throw Error('unsafe_debug_directory');
 const cutoff=now-retentionDays*86400000;let removed=0;
 for(const entry of (await readdir(dir,{withFileTypes:true})).slice(0,500)){
  if(!entry.isFile()||entry.isSymbolicLink()||!entry.name.endsWith('.quo'))continue;
  const id=entry.name.slice(0,-4);
  if(!uuid.test(id))continue;
  const target=debugBundlePath(root,id);
  const info=await lstat(target).catch(e=>{if((e as NodeJS.ErrnoException).code==='ENOENT')return null;throw e});
  if(!info||!info.isFile()||info.isSymbolicLink()||Math.max(info.mtimeMs,info.ctimeMs)>=cutoff)continue;
  const row=await db.query('SELECT 1 FROM debug_submissions WHERE id=$1',[id]);
  if(row.rowCount)continue;
  const verify=await lstat(target).catch(()=>null);
  if(!verify||!verify.isFile()||verify.isSymbolicLink()||Math.max(verify.mtimeMs,verify.ctimeMs)>=cutoff)continue;
  await unlink(target);removed++;
 }
 return removed;
}
