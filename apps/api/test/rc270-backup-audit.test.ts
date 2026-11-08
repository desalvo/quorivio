import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,writeFile,mkdir,rm,stat} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {allowedBackupBackends,validateBackupTarget,sealBackupConfig,openBackupConfig,publicBackupConfig} from '../src/backup-storage.ts';
import {auditOperation,validAuditRetention} from '../src/operation-audit.ts';
import {signS3Request,multipartS3Backup} from '../src/s3-backup.ts';
import {pgDumpEnvironment,buildFullBackup,uploadBackup} from '../src/full-backup.ts';
import {ldapSettingsFromEnv,adminDirectorySearchFilter} from '../src/ldap-auth.ts';
const env={QUORIVIO_BACKUP_ALLOWED_BACKENDS:'posix,nfs,s3,webdav',QUORIVIO_BACKUP_POSIX_ROOT:'/backup/posix',QUORIVIO_BACKUP_NFS_ROOT:'/backup/nfs'};
test('enabled backends and safe mounted paths / remote locations',()=>{
 assert.deepEqual(allowedBackupBackends(env),['posix','nfs','s3','webdav']);
 assert.deepEqual(allowedBackupBackends({}),[]);
 assert.equal(validateBackupTarget({backend:'posix',directory:'daily/2026'},env).directory,'daily/2026');
 for(const directory of ['../secrets','/etc/passwd','a/../b','../../root','foo//bar'])assert.throws(()=>validateBackupTarget({backend:'nfs',directory},env));
 assert.throws(()=>validateBackupTarget({backend:'posix'}, {QUORIVIO_BACKUP_ALLOWED_BACKENDS:'s3'}));
 assert.throws(()=>validateBackupTarget({backend:'webdav',url:'http://insecure'},env));
 assert.throws(()=>validateBackupTarget({backend:'webdav',url:'https://user:pass@host/'},env));
 assert.equal(validateBackupTarget({backend:'s3',bucket:'quorivio-backups',region:'eu-west-1',accessKey:'KEY',secretKey:'PASSWORD'},env).bucket,'quorivio-backups');
 assert.throws(()=>validateBackupTarget({backend:'s3',bucket:'quorivio-backups',region:'eu-west-1',accessKey:'KEY'},env));
});
test('encrypted stored backup secrets never exposed by admin GET',()=>{
 const t=validateBackupTarget({backend:'webdav',url:'https://storage.example.org/backups',username:'admin',password:'pass!'},env);
 const blob=sealBackupConfig(t,'x'.repeat(40));assert.equal(blob.includes('pass!'),false);
 assert.deepEqual(openBackupConfig(blob,'x'.repeat(40)),t);
 assert.throws(()=>openBackupConfig(blob,'y'.repeat(40)));
 assert.equal(JSON.stringify(publicBackupConfig(t)).includes('pass!'),false);
});
test('audited write methods, redaction and bounded retention',()=>{
 assert.deepEqual(auditOperation('PUT','/api/admin/backups',200),{action:'put',resource_type:'/api/admin/backups'});
 assert.equal(auditOperation('GET','/api/admin/backups',200),null);
 assert.equal(auditOperation('POST','/api/auth/login',200),null);
 assert.equal(auditOperation('POST','/api/admin/users',401),null);
 assert.equal(validAuditRetention(7),true);assert.equal(validAuditRetention(365),true);
 for(const bad of [6,3651,10.1,'30'])assert.equal(validAuditRetention(bad),false);
});
test('administrator LDAP lookup escapes filters and supports username / email prefixes',()=>{
 const settings=ldapSettingsFromEnv({LDAP_URL:'ldaps://example.org',LDAP_BIND_DN:'cn=admin',LDAP_BIND_PASSWORD:'secret',LDAP_BASE_DN:'dc=example,dc=org'})!;
 const filter=adminDirectorySearchFilter(settings,'admin*)(x');
 assert.match(filter,/\\2a/);assert.match(filter,/sAMAccountName=/);
 assert.throws(()=>adminDirectorySearchFilter(settings,'*'));
});
test('AWS V4 signing is deterministic and token changes signed headers',()=>{
 const args={method:'POST',url:'https://s3.eu-west-1.amazonaws.com/quorivio-backups/dump.tar.gz?uploads=',region:'eu-west-1',accessKey:'AKIAEXAMPLE',secretKey:'TESTONLYSECRET',payload:Buffer.from(''),date:new Date('2026-11-08T15:16:17.000Z')};
 const signature=signS3Request(args);
 assert.match(signature.Authorization,/Credential=AKIAEXAMPLE\/20261108\/eu-west-1\/s3\/aws4_request/);
 assert.equal(signature['x-amz-date'],'20261108T151617Z');
 assert.equal(signature['x-amz-content-sha256'],createHash('sha256').update('').digest('hex'));
 assert.deepEqual(signS3Request(args),signature);
 assert.notEqual(signS3Request({...args,token:'TOKEN'}).Authorization,signature.Authorization);
});
test('pg_dump receives credentials only through env, not command args',()=>{
 const e=pgDumpEnvironment('postgresql://alice:p%40ss%21@db.internal:5433/quorivio?sslmode=require',{});
 assert.equal(e.PGPASSWORD,'p@ss!');assert.equal(e.PGHOST,'db.internal');assert.equal(e.PGSSLMODE,'require');
});
test('complete archive includes custom-format database dump and assets; POSIX atomic upload',async()=>{
 const base=await mkdtemp(path.join(tmpdir(),'quorivio-rc270-test-'));
 const assets=path.join(base,'assets'),bin=path.join(base,'bin'),destination=path.join(base,'backups');
 await mkdir(assets);await mkdir(bin);await mkdir(destination);await mkdir(path.join(assets,'session-test'));
 await writeFile(path.join(assets,'session-test','asset.txt'),'required-data');
 await writeFile(path.join(bin,'pg_dump'),`#!/bin/sh
for a in "$@"; do case "$a" in --file=*) f="\${a#--file=}";; esac; done
printf 'fake-custom-postgres-dump' > "$f"
`,{mode:0o755});
 const before=process.env.PATH;process.env.PATH=bin+':'+before;
 let full:null|Awaited<ReturnType<typeof buildFullBackup>>=null;
 try{
  full=await buildFullBackup('postgresql://test:test@localhost/quorivio',assets);
  const list=execFileSync('tar',['-tzf',full.archive],{encoding:'utf8'});
  assert.match(list,/database.dump/);assert.match(list,/manifest.json/);assert.match(list,/assets\/session-test\/asset.txt/);
  assert.equal(full.sha256,createHash('sha256').update(await readFile(full.archive)).digest('hex'));
  await uploadBackup({backend:'posix',directory:'nightly'},{archive:full.archive,name:full.name},{...env,QUORIVIO_BACKUP_POSIX_ROOT:destination});
  assert.equal((await stat(path.join(destination,'nightly',full.name))).size,full.size);
 }finally{process.env.PATH=before;if(full)await rm(full.directory,{recursive:true,force:true});await rm(base,{recursive:true,force:true})}
});

test('S3 upload streams multipart parts over signed HTTPS requests and commits manifest',async()=>{
 const base=await mkdtemp(path.join(tmpdir(),'quorivio-s3-'));
 const file=path.join(base,'archive.tar.gz');await writeFile(file,Buffer.alloc(9*1024*1024,3));
 const target=validateBackupTarget({backend:'s3',bucket:'unit-backups',region:'us-east-1',accessKey:'ACCESS',secretKey:'SECRET'},env);
 const requests:{url:string;method:string;authorization:string}[]=[];
 const previous=globalThis.fetch;
 globalThis.fetch=(async(input:any,init:any)=>{
  const url=String(input);requests.push({url,method:init.method,authorization:init.headers.Authorization});
  if(url.endsWith('?uploads='))return new Response('<InitiateMultipartUploadResult><UploadId>test-upload</UploadId></InitiateMultipartUploadResult>',{status:200});
  if(init.method==='PUT')return new Response(null,{status:200,headers:{ETag:'"testing"'}});
  return new Response('<CompleteMultipartUploadResult/>',{status:200});
 }) as typeof fetch;
 try{
  await multipartS3Backup(target,{archive:file,name:'archive.tar.gz'});
  assert.deepEqual(requests.map(r=>r.method),['POST','PUT','PUT','POST']);
  assert.ok(requests.every(r=>r.url.startsWith('https://')&&r.authorization.startsWith('AWS4-HMAC-SHA256')));
  assert.ok(requests[3].url.includes('uploadId=test-upload'));
 }finally{globalThis.fetch=previous;await rm(base,{recursive:true,force:true})}
});
test('WebDAV backup prohibits redirect and sends TLS authenticated upload with exact size',async()=>{
 const base=await mkdtemp(path.join(tmpdir(),'quorivio-webdav-'));const file=path.join(base,'archive.tar.gz');await writeFile(file,'fake-backup');
 const previous=globalThis.fetch;let seen:any=null;
 globalThis.fetch=(async(url:any,init:any)=>{seen={url:String(url),init};return new Response(null,{status:201})}) as typeof fetch;
 try{
  await uploadBackup({backend:'webdav',url:'https://webdav.example.org/backups',username:'admin',password:'password'},{archive:file,name:'archive.tar.gz'});
  assert.equal(seen.url,'https://webdav.example.org/backups/archive.tar.gz');
  assert.equal(seen.init.redirect,'manual');assert.equal(seen.init.headers['Content-Length'],'11');
  assert.match(seen.init.headers.Authorization,/^Basic /);
  globalThis.fetch=(async()=>new Response(null,{status:302,headers:{location:'https://attacker.test/'}})) as typeof fetch;
  await assert.rejects(uploadBackup({backend:'webdav',url:'https://webdav.example.org/backups'},{archive:file,name:'archive.tar.gz'}),/webdav_upload_failed_302/);
 }finally{globalThis.fetch=previous;await rm(base,{recursive:true,force:true})}
});
