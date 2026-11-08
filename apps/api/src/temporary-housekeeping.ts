/** RC269 scheduled space reclamation. Never delete any registered asset, library
 * background or profile photo. Unknown files and symlinks are preserved rather
 * than guessing their ownership. Age alone is never enough for library media. */
import {readdir,lstat,rm,unlink} from 'node:fs/promises';
import path from 'node:path';

const jobName=/^[a-f0-9]{32}$/i;
const uuid=/^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
export const HOUSEKEEPING_PERIOD_MS=12*60*60*1000;
export type HousekeepingStats={expiredWorkspaces:number;orphanFiles:number;preserved:number};

/** Check not only the job directory's mtime: writing an existing nested output
 * does not change its parent's mtime. An excessive/deep tree is fail-closed. */
async function isStaleTree(dir:string,cutoff:number,depth=0,budget={count:0}):Promise<boolean>{
 if(depth>8||budget.count++>10000)return false;
 const st=await lstat(dir);
 if(st.isSymbolicLink()||(!st.isDirectory()&&!st.isFile()))return false;
 if(Math.max(st.mtimeMs,st.ctimeMs)>=cutoff)return false;
 if(st.isDirectory()){
  for(const entry of await readdir(dir,{withFileTypes:true})){
   // The isolated converter creates this reservation for active jobs. Even a
   // long-running job older than the TTL must never be removed while locked.
   if(entry.name==='.conversion-lock')return false;
   if(entry.isSymbolicLink()||(!entry.isDirectory()&&!entry.isFile()))return false;
   if(!await isStaleTree(path.join(dir,entry.name),cutoff,depth+1,budget))return false;
  }
 }
 return true;
}
/** Conversion roots are ephemeral pod-local volumes. Workspaces use unpredictable
 * hex IDs and are not reusable/library content. Active jobs are exempt. */
export async function removeExpiredConversionJobs(root:string,now=Date.now(),active:ReadonlySet<string>=new Set()):Promise<number>{
 let deleted=0;let entries;
 try{entries=await readdir(root,{withFileTypes:true})}catch(e){if((e as NodeJS.ErrnoException).code==='ENOENT')return 0;throw e}
 if((await lstat(root)).isSymbolicLink())throw Error('unsafe_conversion_root_symlink');
 const cutoff=now-HOUSEKEEPING_PERIOD_MS;
 for(const entry of entries.slice(0,10000)){
  if(!entry.isDirectory()||entry.isSymbolicLink()||!jobName.test(entry.name))continue;
  const candidate=path.join(root,entry.name);
  if(active.has(candidate))continue;
  try{if(!await isStaleTree(candidate,cutoff))continue;
   if(active.has(candidate))continue;
   await rm(candidate,{recursive:true,force:true,maxRetries:2});deleted++;
  }catch(e){if((e as NodeJS.ErrnoException).code!=='ENOENT')throw e}
 }
 return deleted;
}
/** Only files with a missing authoritative session_assets row are removable;
 * all other directories (background-library, profile-photos, unknown) stay intact.
 * The callback must fail closed on unavailable PostgreSQL, not return false. */
export async function removeOrphanSessionAssetFiles(root:string,isRegistered:(sessionId:string,assetId:string)=>Promise<boolean>,now=Date.now()):Promise<number>{
 let deleted=0;let sessions;
 try{sessions=await readdir(root,{withFileTypes:true})}catch(e){if((e as NodeJS.ErrnoException).code==='ENOENT')return 0;throw e}
 if((await lstat(root)).isSymbolicLink())throw Error('unsafe_asset_root_symlink');
 const cutoff=now-HOUSEKEEPING_PERIOD_MS;
 for(const session of sessions.slice(0,10000)){
  if(!session.isDirectory()||session.isSymbolicLink()||!uuid.test(session.name))continue;
  const folder=path.join(root,session.name);
  const files=await readdir(folder,{withFileTypes:true}).catch(e=>{if((e as NodeJS.ErrnoException).code==='ENOENT')return [];throw e});
  for(const file of files.slice(0,10000)){
   if(!file.isFile()||file.isSymbolicLink()||!uuid.test(file.name))continue;
   const target=path.join(folder,file.name);const st=await lstat(target).catch(e=>{if((e as NodeJS.ErrnoException).code==='ENOENT')return null;throw e});
   if(!st||!st.isFile()||Math.max(st.mtimeMs,st.ctimeMs)>=cutoff)continue;
   if(await isRegistered(session.name,file.name))continue;
   // Recheck before unlink; a concurrent upload may have committed metadata.
   if(await isRegistered(session.name,file.name))continue;
   const fresh=await lstat(target).catch(()=>null);
   if(!fresh||!fresh.isFile()||Math.max(fresh.mtimeMs,fresh.ctimeMs)>=cutoff)continue;
   await unlink(target);deleted++;
  }
 }
 return deleted;
}
