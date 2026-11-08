import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,stat,lstat,rm,symlink} from 'node:fs/promises';
import os from 'node:os';import path from 'node:path';
import {escapeLdapFilter,ldapSettingsFromEnv,ldapUserFilter,directoryAccountRole} from '../src/ldap-auth.ts';
import {removeExpiredConversionJobs,removeOrphanSessionAssetFiles,HOUSEKEEPING_PERIOD_MS} from '../src/temporary-housekeeping.ts';

test('LDAPS verifies certificates, rejects plaintext LDAP, and does not trust email identity implicitly',()=>{
 assert.throws(()=>ldapSettingsFromEnv({LDAP_URL:'ldap://ldap.test',LDAP_BIND_DN:'cn=svc',LDAP_BIND_PASSWORD:'pw',LDAP_BASE_DN:'dc=test'}),/ldap_requires_starttls/);
 assert.throws(()=>ldapSettingsFromEnv({LDAP_URL:'ldaps://ldap.test',LDAP_STARTTLS:'true',LDAP_BIND_DN:'cn=svc',LDAP_BIND_PASSWORD:'pw',LDAP_BASE_DN:'dc=test'}),/ldaps_cannot_starttls/);
 assert.throws(()=>ldapSettingsFromEnv({LDAP_URL:'ldaps://ldap.test',LDAP_BIND_DN:'cn=svc',LDAP_BIND_PASSWORD:'pw',LDAP_BASE_DN:'dc=test',LDAP_AUTO_PROVISION:'true'}),/ldap_provision_requires_organization_id/);
 assert.equal(ldapSettingsFromEnv({}),null);
 const settings=ldapSettingsFromEnv({LDAP_URL:'ldaps://ldap.test:636',LDAP_BIND_DN:'cn=svc',LDAP_BIND_PASSWORD:'pw',LDAP_BASE_DN:'dc=test',LDAP_PRESENTER_GROUP_DN:'cn=presenters',LDAP_ADMIN_GROUP_DN:'cn=admins'})!;
 assert.equal(settings.url,'ldaps://ldap.test:636');
 assert.equal(ldapUserFilter(settings,'a*)(uid=*)'),'(uid=a\\2a\\29\\28uid=\\2a\\29)');
 assert.equal(escapeLdapFilter('a\\b'),'a\\5cb');
 assert.equal(directoryAccountRole(settings,['CN=PRESENTERS']),'presenter');
 assert.equal(directoryAccountRole(settings,['cn=admins']),'org_admin');
 assert.equal(directoryAccountRole(settings,[]),'user');
});

test('12h conversion cleanup keeps recent, unknown, active and symlinked workspaces',async()=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'quorivio-housekeeping-'));
 const expired='a'.repeat(32),recent='b'.repeat(32),active='c'.repeat(32),locked='e'.repeat(32);
 try{
  for(const d of [expired,recent,active,locked]){await mkdir(path.join(root,d));await writeFile(path.join(root,d,'file'),'sample')}
  await mkdir(path.join(root,locked,'.conversion-lock')); 
  await mkdir(path.join(root,'human-named-folder'));
  await symlink(path.join(root,expired),path.join(root,'d'.repeat(32)));
  const later=Date.now()+HOUSEKEEPING_PERIOD_MS+60000;
  const removed=await removeExpiredConversionJobs(root,later,new Set([path.join(root,active)]));
  assert.equal(removed,2); // expired and recent become stale at a simulated 12h future clock
  await assert.rejects(stat(path.join(root,expired)),{code:'ENOENT'});
  await stat(path.join(root,active));await stat(path.join(root,locked));await stat(path.join(root,'human-named-folder'));
  await lstat(path.join(root,'d'.repeat(32)));
 }finally{await rm(root,{recursive:true,force:true})}
});

test('persistent files are never purged if registered; unknown library folders untouched',async()=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'quorivio-assets-'));
 const session='123e4567-e89b-42d3-a456-426614174000';
 const used='123e4567-e89b-42d3-a456-426614174001';const unused='123e4567-e89b-42d3-a456-426614174002';
 try{
  await mkdir(path.join(root,session));await mkdir(path.join(root,'background-library'));
  await writeFile(path.join(root,session,used),'used');await writeFile(path.join(root,session,unused),'orphan');
  await writeFile(path.join(root,'background-library','saved'),'important');
  const calls:string[]=[];
  const removed=await removeOrphanSessionAssetFiles(root,async(_sid,aid)=>{calls.push(aid);return aid===used},Date.now()+HOUSEKEEPING_PERIOD_MS+60000);
  assert.equal(removed,1);assert.ok(calls.includes(used));
  await stat(path.join(root,session,used));await stat(path.join(root,'background-library','saved'));
  await assert.rejects(stat(path.join(root,session,unused)),{code:'ENOENT'});
 }finally{await rm(root,{recursive:true,force:true})}
});
