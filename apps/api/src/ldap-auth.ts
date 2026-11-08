/** RC269 LDAP/LDAPS directory authentication, opt-in. No plaintext password
 * transport, disabled certificate verification, or silent email-based linking. */
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
export type LdapSettings={url:string;startTls:boolean;bindDn:string;bindPassword:string;baseDn:string;filter:string;idAttribute:string;emailAttribute:string;groupAttribute:string;adminGroupDn:string;presenterGroupDn:string;organizationId:string;autoProvision:boolean;caFile:string;label:string};
export function escapeLdapFilter(value:string):string{
 return value.replace(/[\\*()\x00]/g,c=>({ '\\':'\\5c','*':'\\2a','(':'\\28',')':'\\29','\x00':'\\00'}[c]||''));
}
export function ldapSettingsFromEnv(env:NodeJS.ProcessEnv=process.env):LdapSettings|null{
 if(!env.LDAP_URL)return null;
 const url=new URL(env.LDAP_URL);
 if(!['ldap:','ldaps:'].includes(url.protocol)||!url.hostname||(url.pathname!==''&&url.pathname!=='/')||url.username||url.password||url.search||url.hash)throw Error('invalid_ldap_url');
 const startTls=env.LDAP_STARTTLS==='true';
 if(url.protocol==='ldap:'&&!startTls)throw Error('ldap_requires_starttls');
 if(url.protocol==='ldaps:'&&startTls)throw Error('ldaps_cannot_starttls');
 const filter=env.LDAP_USER_FILTER||'(uid={login})';
 if(filter.split('{login}').length!==2||filter.length>512||/[\x00-\x1f]/.test(filter))throw Error('invalid_ldap_filter');
 const baseDn=env.LDAP_BASE_DN?.trim()||'';
 if(!baseDn||!env.LDAP_BIND_DN||!env.LDAP_BIND_PASSWORD)throw Error('ldap_service_bind_required');
 const autoProvision=env.LDAP_AUTO_PROVISION==='true';
 const organizationId=env.LDAP_ORGANIZATION_ID?.trim()||'';
 if(autoProvision&&!/^[a-f\d]{8}-(?:[a-f\d]{4}-){3}[a-f\d]{12}$/i.test(organizationId))throw Error('ldap_provision_requires_organization_id');
 for(const key of ['LDAP_ID_ATTRIBUTE','LDAP_EMAIL_ATTRIBUTE','LDAP_GROUP_ATTRIBUTE'])if(env[key]&&!/^[a-z][a-z0-9-]{0,63}$/i.test(env[key]!))throw Error('invalid_ldap_attribute');
 return {url:url.href.replace(/\/$/,''),startTls,bindDn:env.LDAP_BIND_DN,bindPassword:env.LDAP_BIND_PASSWORD,baseDn,filter,
  idAttribute:env.LDAP_ID_ATTRIBUTE||'entryUUID',emailAttribute:env.LDAP_EMAIL_ATTRIBUTE||'mail',groupAttribute:env.LDAP_GROUP_ATTRIBUTE||'memberOf',
  adminGroupDn:env.LDAP_ADMIN_GROUP_DN||'',presenterGroupDn:env.LDAP_PRESENTER_GROUP_DN||'',organizationId,autoProvision,
  caFile:env.LDAP_TLS_CA_FILE||'',label:(env.LDAP_LABEL||'LDAP / Active Directory').slice(0,80)};
}
export function ldapUserFilter(settings:LdapSettings,login:string):string{
 if(login.length<1||login.length>254||/[\x00-\x1f]/.test(login))throw Error('invalid_ldap_login');
 return settings.filter.replace('{login}',escapeLdapFilter(login));
}
export function directoryAccountRole(settings:LdapSettings,groups:string[]):'org_admin'|'presenter'|'user'{
 const normalized=new Set(groups.map(x=>x.toLowerCase().trim()));
 if(settings.adminGroupDn&&normalized.has(settings.adminGroupDn.toLowerCase().trim()))return 'org_admin';
 if(settings.presenterGroupDn&&normalized.has(settings.presenterGroupDn.toLowerCase().trim()))return 'presenter';
 return settings.presenterGroupDn||settings.adminGroupDn?'user':'presenter';
}
export type LdapAuthenticatedUser={subject:string;email:string;role:'org_admin'|'presenter'|'user'};
function attribute(value:unknown):string{
 if(Buffer.isBuffer(value))return value.toString('hex');
 if(typeof value==='string')return value;
 if(Array.isArray(value))return attribute(value[0]);
 return '';
}
function values(value:unknown):string[]{return (Array.isArray(value)?value:[value]).map(attribute).filter(Boolean)}
export async function authenticateDirectory(settings:LdapSettings,login:string,password:string):Promise<LdapAuthenticatedUser|null>{
 if(!password||password.length>1024||password.includes('\x00'))return null;
 // Deferred import: no LDAP transport is initialized when the feature is disabled.
 const {Client}=await import('ldapts');
 const tlsOptions={rejectUnauthorized:true,minVersion:'TLSv1.2' as const,...(settings.caFile?{ca:[readFileSync(settings.caFile)]}:{})};
 const client=new Client({url:settings.url,timeout:8000,connectTimeout:5000,tlsOptions});
 try{
  if(settings.startTls)await client.startTLS(tlsOptions);
  await client.bind(settings.bindDn,settings.bindPassword);
  const result=await client.search(settings.baseDn,{scope:'sub',filter:ldapUserFilter(settings,login),attributes:[settings.idAttribute,settings.emailAttribute,settings.groupAttribute],sizeLimit:2,timeLimit:5});
  if(result.searchEntries.length!==1)return null;
  const entry=result.searchEntries[0];
  const dn=attribute(entry.dn);if(!dn)return null;
  const subject=attribute(entry[settings.idAttribute]);
  const email=attribute(entry[settings.emailAttribute]).trim().toLowerCase();
  if(!subject||subject.length>512||!/^\S+@\S+\.\S+$/.test(email)||email.length>254)return null;
  const groups=values(entry[settings.groupAttribute]);
  // Bind as the selected directory DN to verify the password; never treat a
  // successful service search as proof of user authentication.
  await client.bind(dn,password);
  return {subject:settings.idAttribute.toLowerCase()==='objectguid'?createHash('sha256').update(subject).digest('hex'):subject,email,role:directoryAccountRole(settings,groups)};
 }catch(e){
  if(e instanceof Error&&/InvalidCredentials|invalid credentials|Invalid DN Syntax/i.test(e.message))return null;
  throw e;
 }finally{await client.unbind().catch(()=>{});}
}

/** Escaped prefix matches for administrator lookup; limited to ten directory entries. */
export function adminDirectorySearchFilter(settings:LdapSettings,query:string):string{
 if(query.length<2||query.length>120||/[\x00-\x1f]/.test(query))throw Error('invalid_ldap_search');
 const term=escapeLdapFilter(query.trim());if(term.length<2)throw Error('invalid_ldap_search');
 return `(|(${settings.emailAttribute}=${term}*)(uid=${term}*)(cn=${term}*)(sAMAccountName=${term}*))`;
}
/** Administrators may look up directory identities; a service bind alone never authenticates a user. */
export async function searchDirectory(settings:LdapSettings,query:string):Promise<Array<{subject:string;email:string}>>{
 const filter=adminDirectorySearchFilter(settings,query);
 const {Client}=await import('ldapts');
 const tlsOptions={rejectUnauthorized:true,minVersion:'TLSv1.2' as const,...(settings.caFile?{ca:[readFileSync(settings.caFile)]}:{})};
 const client=new Client({url:settings.url,timeout:8000,connectTimeout:5000,tlsOptions});
 try{
  if(settings.startTls)await client.startTLS(tlsOptions);
  await client.bind(settings.bindDn,settings.bindPassword);
  const entries=await client.search(settings.baseDn,{scope:'sub',filter,attributes:[settings.idAttribute,settings.emailAttribute],sizeLimit:10,timeLimit:5});
  return entries.searchEntries.map(entry=>{
   const raw=attribute(entry[settings.idAttribute]);const subject=settings.idAttribute.toLowerCase()==='objectguid'?createHash('sha256').update(raw).digest('hex'):raw;
   return {subject,email:attribute(entry[settings.emailAttribute]).trim().toLowerCase()};
  }).filter(x=>x.subject&&x.subject.length<=512&&/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(x.email)&&x.email.length<=254);
 }finally{await client.unbind().catch(()=>{})}
}
