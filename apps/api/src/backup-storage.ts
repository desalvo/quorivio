/** Full-instance backup configuration, deployment-controlled mounts and sealed credentials.
 * No restore endpoint: restore requires stopping writes and DBA/operator review. */
import {createCipheriv,createDecipheriv,createHash,randomBytes} from 'node:crypto';
export type BackupBackend='posix'|'nfs'|'s3'|'webdav';
export type BackupTarget={backend:BackupBackend;directory?:string;bucket?:string;region?:string;endpoint?:string;prefix?:string;accessKey?:string;secretKey?:string;url?:string;username?:string;password?:string};
const segment=/^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$/;
const validPrefix=(v:string)=>v===''||v.split('/').every(p=>p!=='.'&&p!=='..'&&segment.test(p));
export function allowedBackupBackends(env:NodeJS.ProcessEnv=process.env):BackupBackend[]{
 const supported:['posix','nfs','s3','webdav']=['posix','nfs','s3','webdav'];
 const allowed=(env.QUORIVIO_BACKUP_ALLOWED_BACKENDS||'').split(',').map(x=>x.trim()).filter(Boolean);
 return supported.filter(x=>allowed.includes(x));
}
export function validateBackupTarget(value:any,env:NodeJS.ProcessEnv=process.env):BackupTarget{
 const backend=value?.backend;
 if(!['posix','nfs','s3','webdav'].includes(backend)||!allowedBackupBackends(env).includes(backend))throw Error('backup_backend_disabled');
 if(backend==='posix'||backend==='nfs'){
  const root=backend==='posix'?env.QUORIVIO_BACKUP_POSIX_ROOT:env.QUORIVIO_BACKUP_NFS_ROOT;
  if(!root||!root.startsWith('/'))throw Error('backup_volume_unavailable');
  const directory=value?.directory??'';
  if(typeof directory!=='string'||directory.length>160||!validPrefix(directory))throw Error('invalid_backup_directory');
  return {backend,directory};
 }
 if(backend==='s3'){
  const bucket=value?.bucket,region=value?.region||'us-east-1',prefix=value?.prefix||'',endpoint=value?.endpoint||'';
  if(typeof bucket!=='string'||!/^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$/.test(bucket)||!/^[-a-z0-9]{2,40}$/.test(region)||typeof prefix!=='string'||prefix.length>240||!validPrefix(prefix))throw Error('invalid_s3_target');
  if(endpoint&&(typeof endpoint!=='string'||!endpoint.startsWith('https://')||new URL(endpoint).username||new URL(endpoint).password))throw Error('invalid_s3_endpoint');
  const accessKey=value?.accessKey||'',secretKey=value?.secretKey||'';
  if(typeof accessKey!=='string'||typeof secretKey!=='string'||Boolean(accessKey)!==Boolean(secretKey)||accessKey.length>200||secretKey.length>256)throw Error('invalid_s3_credentials');
  return {backend,bucket,region,prefix,endpoint,accessKey,secretKey};
 }
 const url=value?.url,username=value?.username||'',password=value?.password||'';
 if(typeof url!=='string'||url.length>1024||!url.startsWith('https://'))throw Error('invalid_webdav_url');
 const parsed=new URL(url);
 if(parsed.username||parsed.password||parsed.search||parsed.hash||!parsed.hostname||parsed.port==='0')throw Error('invalid_webdav_url');
 if(typeof username!=='string'||typeof password!=='string'||username.length>200||password.length>256)throw Error('invalid_webdav_credentials');
 return {backend,url:url.replace(/\/$/,''),username,password};
}
function key(secret:string){return createHash('sha256').update('quorivio-full-backup-v1:').update(secret).digest()}
export function sealBackupConfig(c:BackupTarget,secret:string){const iv=randomBytes(12),cipher=createCipheriv('aes-256-gcm',key(secret),iv);const data=Buffer.concat([cipher.update(JSON.stringify(c)),cipher.final()]);return `v1.${iv.toString('base64url')}.${cipher.getAuthTag().toString('base64url')}.${data.toString('base64url')}`}
export function openBackupConfig(blob:string,secret:string):BackupTarget{
 const parts=blob.split('.');if(parts.length!==4||parts[0]!=='v1')throw Error('invalid_backup_blob');
 const dec=createDecipheriv('aes-256-gcm',key(secret),Buffer.from(parts[1],'base64url'));dec.setAuthTag(Buffer.from(parts[2],'base64url'));
 return JSON.parse(Buffer.concat([dec.update(Buffer.from(parts[3],'base64url')),dec.final()]).toString('utf8'));
}
export function publicBackupConfig(c:BackupTarget|null){return c?{backend:c.backend,directory:c.directory,bucket:c.bucket,region:c.region,prefix:c.prefix,endpoint:c.endpoint,accessKey:c.accessKey,url:c.url,username:c.username,credentials_configured:Boolean(c.secretKey||c.password),password_configured:Boolean(c.password)}:null}
