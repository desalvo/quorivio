/** Runtime-complete PostgreSQL+persisted-file archive, streamed or uploaded.
 * PostgreSQL's custom dump can be restored with pg_restore and files with tar.
 * The asset directory must be immutable or snapshotted during archive creation
 * for strong point-in-time guarantees across both data stores. */
import {spawn} from 'node:child_process';
import {createHash,randomUUID} from 'node:crypto';
import {createReadStream,createWriteStream} from 'node:fs';
import {mkdir,mkdtemp,readFile,rm,stat,writeFile,copyFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pipeline} from 'node:stream/promises';
import type {BackupTarget} from './backup-storage.js';

export async function runProgram(program:string,args:string[],env:NodeJS.ProcessEnv=process.env){
 await new Promise<void>((resolve,reject)=>{
  const child=spawn(program,args,{env,stdio:['ignore','ignore','pipe'],signal:AbortSignal.timeout(30*60*1000)});
  let stderr='';child.stderr.on('data',b=>{stderr=(stderr+String(b)).slice(-2048)});
  child.on('error',reject);child.on('close',code=>code===0?resolve():reject(Error(`${program}_failed_${code}`)));
 });
}
export function pgDumpEnvironment(databaseUrl:string,base:NodeJS.ProcessEnv=process.env):NodeJS.ProcessEnv{
 const u=new URL(databaseUrl);
 if(!['postgresql:','postgres:'].includes(u.protocol)||!u.hostname)throw Error('invalid_postgres_connection');
 return {...base,PGHOST:u.hostname,PGPORT:u.port||'5432',PGUSER:decodeURIComponent(u.username),PGPASSWORD:decodeURIComponent(u.password),PGDATABASE:decodeURIComponent(u.pathname.slice(1)),PGSSLMODE:u.searchParams.get('sslmode')||'prefer'};
}
export async function buildFullBackup(databaseUrl:string,assetsRoot:string):Promise<{archive:string;directory:string;size:number;sha256:string;name:string}>{
 const directory=await mkdtemp(path.join(tmpdir(),'quorivio-full-backup-'));
 try{
  const dump=path.join(directory,'database.dump');
  await runProgram('pg_dump',['--format=custom','--no-owner','--no-privileges','--file='+dump],pgDumpEnvironment(databaseUrl));
  const metadata={format:'quorivio-full-instance-backup',version:1,created_at:new Date().toISOString(),database:'database.dump',assets:'assets/',restore:'pg_restore --clean --if-exists; extract assets/ into persistent asset root; use an offline maintenance window for restore',limitations:'asset files and pg_dump are not an atomic cross-store snapshot unless writes are quiesced'};
  await writeFile(path.join(directory,'manifest.json'),JSON.stringify(metadata,null,2),{mode:0o600});
  const name=`quorivio-full-${new Date().toISOString().replace(/[:.]/g,'-')}-${randomUUID().slice(0,8)}.tar.gz`;
  const archive=path.join(directory,name);
  await runProgram('tar',['-czf',archive,'-C',directory,'database.dump','manifest.json','-C',path.dirname(assetsRoot),path.basename(assetsRoot)]);
  const size=(await stat(archive)).size;
  const sha256=await new Promise<string>((resolve,reject)=>{const dig=createHash('sha256');const r=createReadStream(archive);r.on('data',b=>dig.update(b));r.on('error',reject);r.on('end',()=>resolve(dig.digest('hex')))});
  return {directory,archive,size,sha256,name};
 }catch(e){await rm(directory,{recursive:true,force:true});throw e}
}
export async function uploadBackup(target:BackupTarget,file:{archive:string;name:string},env:NodeJS.ProcessEnv=process.env):Promise<void>{
 if(target.backend==='posix'||target.backend==='nfs'){
  const root=target.backend==='posix'?env.QUORIVIO_BACKUP_POSIX_ROOT:env.QUORIVIO_BACKUP_NFS_ROOT;
  if(!root)throw Error('backup_volume_unavailable');
  const directory=path.join(root,target.directory||'');
  await mkdir(directory,{recursive:true,mode:0o700});
  // Temp + atomic rename avoids treating an incomplete backup as valid.
  const {rename,open}=await import('node:fs/promises');
  const destination=path.join(directory,file.name),temp=destination+'.partial-'+randomUUID();
  try{
   const h=await open(temp,'wx',0o600);
   try{await pipeline(createReadStream(file.archive),h.createWriteStream())}finally{await h.close().catch(()=>{})}
   await rename(temp,destination);
  }catch(e){await rm(temp,{force:true});throw e}
 }else if(target.backend==='s3'){
  const {multipartS3Backup}=await import('./s3-backup.js');
  await multipartS3Backup(target,file);
 }else if(target.backend==='webdav'){
  const headers:Record<string,string>={'Content-Type':'application/gzip','Content-Length':String((await stat(file.archive)).size)};
  if(target.username&&target.password)headers.Authorization='Basic '+Buffer.from(`${target.username}:${target.password}`).toString('base64');
  // No redirects: prevent credential or data exfiltration to a different host.
  const url=target.url!.replace(/\/$/,'')+'/'+encodeURIComponent(file.name);
  // Node's fetch supports streaming Node Readable bodies with duplex:'half'.
  // DOM RequestInit typings do not describe this Node-specific extension,
  // so validate the runtime fields and narrow only at the fetch boundary.
  const request={method:'PUT',headers,body:createReadStream(file.archive),duplex:'half' as const,redirect:'manual' as const,signal:AbortSignal.timeout(30*60*1000)};
  const reply=await fetch(url,request as unknown as RequestInit);
  if(![200,201,204].includes(reply.status))throw Error('webdav_upload_failed_'+reply.status);
 }else throw Error('unsupported_backup_backend');
}
