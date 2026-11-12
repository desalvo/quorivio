/** RC322: database-backed, opt-in authentication providers.
 * All external providers start DISABLED, including preconfigured env providers.
 * Secrets are encrypted at rest and must never be sent back to the browser.
 */
import type {Pool} from 'pg';
import {createCipheriv,createDecipheriv,createHash,randomBytes} from 'node:crypto';
import {ldapSettingsFromEnv,type LdapSettings} from './ldap-auth.js';
import {providersFromEnv,validProvider,validOidcCallback,validateDiscovery,fetchOidcJson,type OidcProvider} from './oidc.js';
import {socialProviders,type SocialProvider} from './social-oauth.js';
import {validateSsoBranding,publicSsoBranding} from './sso-branding.js';

export type AuthBackendKind='local'|'ldap'|'oidc'|'social';
export type Backend={id:string;kind:AuthBackendKind;enabled:boolean;mfaEnabled:boolean;config:Record<string,any>;lastTestedAt:string|null};
export type PublicBackend={id:string;kind:AuthBackendKind;enabled:boolean;mfaEnabled:boolean;configured:boolean;lastTestedAt:string|null;config:Record<string,any>;hasSecret:boolean};
const BACKEND_ID=/^[a-z][a-z0-9_-]{1,31}$/;
const secretFields=new Set(['bindPassword','clientSecret']);
const configFields:Record<AuthBackendKind,string[]>={
 local:[],
 ldap:['url','startTls','bindDn','bindPassword','baseDn','filter','idAttribute','emailAttribute','groupAttribute','adminGroupDn','presenterGroupDn','organizationId','autoProvision','caFile','label'],
 oidc:['issuer','clientId','clientSecret','redirectUri','label','logoData','buttonColor'],
 social:['clientId','clientSecret','redirectUri','label','buttonColor']
};
function key(secret:string){return createHash('sha256').update('quorivio-auth-backends-v1:').update(secret).digest()}
export function sealAuthConfig(data:Record<string,any>,secret:string):string{
 const iv=randomBytes(12),cipher=createCipheriv('aes-256-gcm',key(secret),iv);
 const payload=Buffer.concat([cipher.update(JSON.stringify(data),'utf8'),cipher.final()]);
 return ['v1',iv.toString('base64url'),cipher.getAuthTag().toString('base64url'),payload.toString('base64url')].join('.');
}
export function openAuthConfig(data:string,secret:string):Record<string,any>{
 const parts=data.split('.');
 if(parts.length!==4||parts[0]!=='v1')throw Error('invalid_auth_backend_blob');
 const iv=Buffer.from(parts[1],'base64url'),tag=Buffer.from(parts[2],'base64url');
 if(iv.length!==12||tag.length!==16)throw Error('invalid_auth_backend_blob');
 const decipher=createDecipheriv('aes-256-gcm',key(secret),iv);decipher.setAuthTag(tag);
 const decoded=JSON.parse(Buffer.concat([decipher.update(Buffer.from(parts[3],'base64url')),decipher.final()]).toString('utf8'));
 if(!decoded||typeof decoded!=='object'||Array.isArray(decoded))throw Error('invalid_auth_backend_blob');
 return decoded;
}
export function defaultAuthBackends(env:NodeJS.ProcessEnv=process.env):Backend[]{
 const ldap=ldapSettingsFromEnv(env);
 const defaults:Backend[]=[
  {id:'local',kind:'local',enabled:true,mfaEnabled:true,config:{},lastTestedAt:null},
  {id:'ldap',kind:'ldap',enabled:false,mfaEnabled:false,config:ldap||{},lastTestedAt:null},
  {id:'google',kind:'oidc',enabled:false,mfaEnabled:false,config:{label:'Google'},lastTestedAt:null},
  {id:'microsoft',kind:'oidc',enabled:false,mfaEnabled:false,config:{label:'Microsoft Entra ID'},lastTestedAt:null},
  {id:'okta',kind:'oidc',enabled:false,mfaEnabled:false,config:{label:'Okta'},lastTestedAt:null},
  {id:'keycloak',kind:'oidc',enabled:false,mfaEnabled:false,config:{label:'Keycloak'},lastTestedAt:null},
  {id:'authentik',kind:'oidc',enabled:false,mfaEnabled:false,config:{label:'Authentik'},lastTestedAt:null},
  {id:'github',kind:'social',enabled:false,mfaEnabled:false,config:{label:'GitHub'},lastTestedAt:null},
  {id:'facebook',kind:'social',enabled:false,mfaEnabled:false,config:{label:'Facebook'},lastTestedAt:null}
 ];
 for(const p of providersFromEnv(env)){
  const index=defaults.findIndex(x=>x.id===p.id);
  const item:Backend={id:p.id,kind:'oidc',enabled:false,mfaEnabled:false,config:p,lastTestedAt:null};
  if(index>=0)defaults[index]=item;else defaults.push(item);
 }
 for(const p of socialProviders(env)){
  const index=defaults.findIndex(x=>x.id===p.id);
  defaults[index]={id:p.id,kind:'social',enabled:false,mfaEnabled:false,config:{...p,label:p.id==='github'?'GitHub':'Facebook'},lastTestedAt:null};
 }
 return defaults;
}
function expectedKind(id:string):AuthBackendKind{
 if(id==='local')return 'local';
 if(id==='ldap')return 'ldap';
 if(id==='github'||id==='facebook')return 'social';
 if(!BACKEND_ID.test(id))throw Error('invalid_backend_id');
 return 'oidc';
}
export function validateAuthBackend(id:string,kind:AuthBackendKind,config:Record<string,any>):boolean{
 if(expectedKind(id)!==kind)throw Error('invalid_backend_kind');
 if(kind==='local')return true;
 if(kind==='ldap'){
  const settings=ldapSettingsFromEnv({
   LDAP_URL:config.url,LDAP_STARTTLS:config.startTls?'true':'false',
   LDAP_BIND_DN:config.bindDn,LDAP_BIND_PASSWORD:config.bindPassword,
   LDAP_BASE_DN:config.baseDn,LDAP_USER_FILTER:config.filter,
   LDAP_ID_ATTRIBUTE:config.idAttribute,LDAP_EMAIL_ATTRIBUTE:config.emailAttribute,
   LDAP_GROUP_ATTRIBUTE:config.groupAttribute,LDAP_ADMIN_GROUP_DN:config.adminGroupDn,
   LDAP_PRESENTER_GROUP_DN:config.presenterGroupDn,LDAP_ORGANIZATION_ID:config.organizationId,
   LDAP_AUTO_PROVISION:config.autoProvision?'true':'false',LDAP_TLS_CA_FILE:config.caFile,LDAP_LABEL:config.label
  });
  if(!settings)throw Error('ldap_not_configured');
  if(config.label!==undefined&&(typeof config.label!=='string'||!config.label.trim()||config.label.length>80||/[<>\r\n]/.test(config.label)))throw Error('invalid_backend_label');
  if(config.caFile!==undefined&&(typeof config.caFile!=='string'||config.caFile.length>1024))throw Error('invalid_ldap_ca_file');
  return true;
 }
 if(!['oidc','social'].includes(kind))throw Error('invalid_backend_kind');
 validateSsoBranding(id,config);
 const label=config.label;
 if(typeof label!=='string'||!label.trim()||label.length>80||/[<>\r\n]/.test(label))throw Error('invalid_backend_label');
 if(kind==='oidc'){
  const p:OidcProvider={id,issuer:config.issuer,clientId:config.clientId,clientSecret:config.clientSecret,redirectUri:config.redirectUri,label};
  if(!validProvider(p)||!validOidcCallback(p))throw Error('invalid_oidc_backend');
  if(config.issuer.length>1024||config.redirectUri.length>1024||config.clientId.length>512||config.clientSecret.length>2048)throw Error('invalid_oidc_backend');
 }else{
  if(typeof config.clientId!=='string'||!config.clientId||config.clientId.length>512||typeof config.clientSecret!=='string'||!config.clientSecret||config.clientSecret.length>2048||typeof config.redirectUri!=='string'||config.redirectUri.length>1024)throw Error('invalid_social_backend');
  const callback=new URL(config.redirectUri);
  if(callback.protocol!=='https:'||callback.username||callback.password||callback.search||callback.hash||callback.pathname!=='/api/auth/social/'+id)throw Error('invalid_social_callback');
 }
 return true;
}
export function backendPublic(b:Backend):PublicBackend{
 const config=Object.fromEntries(Object.entries(b.config).filter(([k])=>!secretFields.has(k)));
 let configured=false;try{configured=validateAuthBackend(b.id,b.kind,b.config)}catch{}
 return {id:b.id,kind:b.kind,enabled:b.kind==='local'?true:b.enabled,mfaEnabled:b.kind==='local'||b.kind==='ldap'?b.mfaEnabled:false,configured,lastTestedAt:b.lastTestedAt,hasSecret:Boolean(b.config.bindPassword||b.config.clientSecret),config};
}
export async function loadAuthBackends(db:Pool,secret:string,env:NodeJS.ProcessEnv=process.env):Promise<Backend[]>{
 const defaults=defaultAuthBackends(env),byId=new Map(defaults.map(x=>[x.id,x]));
 const rows=await db.query('SELECT id,kind,enabled,mfa_enabled,config_encrypted,last_tested_at FROM auth_backends');
 for(const row of rows.rows){
  const kind=expectedKind(row.id);
  if(row.kind!==kind)throw Error('stored_backend_kind_mismatch');
  const previous=byId.get(row.id);
  const config=row.config_encrypted?openAuthConfig(row.config_encrypted,secret):(previous?.config||{});
  byId.set(row.id,{id:row.id,kind,enabled:kind==='local'?true:row.enabled===true,
   mfaEnabled:kind==='local'||kind==='ldap'?row.mfa_enabled===true:false,config,lastTestedAt:row.last_tested_at?new Date(row.last_tested_at).toISOString():null});
 }
 return [...byId.values()];
}
/** Build the exact effective configuration (including previously sealed credentials) without writing it. */
export async function prepareAuthBackend(db:Pool,secret:string,id:string,input:unknown):Promise<Backend>{
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('invalid_backend_request');
 const body=input as Record<string,any>;
 const kind=expectedKind(id);
 if(body.kind!==kind||typeof body.enabled!=='boolean'||typeof body.mfaEnabled!=='boolean'||(body.config!==undefined&&(!body.config||typeof body.config!=='object'||Array.isArray(body.config))))throw Error('invalid_backend_request');
 if(kind==='local'&&!body.enabled)throw Error('local_backend_cannot_be_disabled');
 if(kind==='oidc'||kind==='social')if(body.mfaEnabled)throw Error('sso_mfa_delegated_to_provider');
 const current=(await loadAuthBackends(db,secret)).find(b=>b.id===id);
 const config={...(current?.config||{})};
 for(const [field,value] of Object.entries(body.config||{})){
  if(!configFields[kind].includes(field)||!(typeof value==='string'||typeof value==='boolean')||typeof value==='string'&&value.length>(field==='logoData'?46000:2048))throw Error('invalid_backend_config');
  if(secretFields.has(field)&&value==='')continue; // preserve the previous encrypted credential
  config[field]=value;
 }
 // Validate branding even for disabled drafts; untrusted images never reach the login page.
 if(kind==='oidc'||kind==='social')validateSsoBranding(id,config);
 // Every enabled backend must have complete, secure configuration.
 if(kind==='local')Object.keys(config).forEach(key=>delete config[key]);
 if(kind!=='local'&&body.enabled)validateAuthBackend(id,kind,config);
 // Validate complete draft configs early, but allow partial disabled drafts.
 if(kind!=='local'&&configFields[kind].every(f=>!['bindPassword','clientSecret','label'].includes(f)||Boolean(config[f]))&&Boolean(config.url||config.issuer||config.clientId)){
  if(kind==='ldap'&&config.url&&config.bindDn&&config.bindPassword&&config.baseDn)validateAuthBackend(id,kind,config);
  if(kind!=='ldap'&&config.clientId&&config.clientSecret&&config.redirectUri&&(kind==='social'||config.issuer))validateAuthBackend(id,kind,config);
 }
 const revised:Backend={id,kind,enabled:kind==='local'?true:body.enabled,mfaEnabled:kind==='local'||kind==='ldap'?body.mfaEnabled:false,config,lastTestedAt:null};
 return revised;
}
/** Only Save persists a draft. Testing uses prepareAuthBackend without storing credentials or changing the active provider. */
export async function saveAuthBackend(db:Pool,secret:string,id:string,input:unknown):Promise<PublicBackend>{
 const revised=await prepareAuthBackend(db,secret,id,input);
 const {kind,config}=revised;
 await db.query("INSERT INTO auth_backends(id,kind,enabled,mfa_enabled,config_encrypted,last_tested_at) VALUES($1,$2,$3,$4,$5,NULL) ON CONFLICT(id) DO UPDATE SET enabled=$3,mfa_enabled=$4,config_encrypted=$5,last_tested_at=NULL,updated_at=now()",
  [id,kind,revised.enabled,revised.mfaEnabled,kind==='local'?'':sealAuthConfig(config,secret)]);
 return backendPublic(revised);
}
export async function enabledLdapBackend(db:Pool,secret:string):Promise<LdapSettings|null>{
 const b=(await loadAuthBackends(db,secret)).find(x=>x.id==='ldap');
 if(!b?.enabled)return null;
 validateAuthBackend(b.id,b.kind,b.config);
 const c=b.config;
 return ldapSettingsFromEnv({LDAP_URL:c.url,LDAP_STARTTLS:c.startTls?'true':'false',LDAP_BIND_DN:c.bindDn,LDAP_BIND_PASSWORD:c.bindPassword,LDAP_BASE_DN:c.baseDn,
  LDAP_USER_FILTER:c.filter,LDAP_ID_ATTRIBUTE:c.idAttribute,LDAP_EMAIL_ATTRIBUTE:c.emailAttribute,LDAP_GROUP_ATTRIBUTE:c.groupAttribute,
  LDAP_ADMIN_GROUP_DN:c.adminGroupDn,LDAP_PRESENTER_GROUP_DN:c.presenterGroupDn,LDAP_ORGANIZATION_ID:c.organizationId,
  LDAP_AUTO_PROVISION:c.autoProvision?'true':'false',LDAP_TLS_CA_FILE:c.caFile,LDAP_LABEL:c.label})!;
}
export async function enabledOidcBackends(db:Pool,secret:string):Promise<OidcProvider[]>{
 return (await loadAuthBackends(db,secret)).filter(x=>x.kind==='oidc'&&x.enabled).map(b=>{validateAuthBackend(b.id,b.kind,b.config);return {...b.config,id:b.id} as OidcProvider});
}
export async function enabledSocialBackends(db:Pool,secret:string):Promise<SocialProvider[]>{
 return (await loadAuthBackends(db,secret)).filter(x=>x.kind==='social'&&x.enabled).map(b=>{validateAuthBackend(b.id,b.kind,b.config);return {id:b.id,clientId:b.config.clientId,clientSecret:b.config.clientSecret,redirectUri:b.config.redirectUri,buttonColor:b.config.buttonColor} as SocialProvider});
}
export async function backendAllowsMfa(db:Pool,secret:string,userId:string):Promise<boolean>{
 const isLdap=(await db.query('SELECT EXISTS(SELECT 1 FROM ldap_identities WHERE user_id=$1) AS ldap',[userId])).rows[0]?.ldap===true;
 const backends=await loadAuthBackends(db,secret);
 return Boolean(backends.find(x=>x.id===(isLdap?'ldap':'local'))?.mfaEnabled);
}
/** Tests do not create sessions or link users, and cannot expose credentials. */
export async function testAuthBackend(db:Pool,secret:string,id:string,draft?:unknown):Promise<{ok:true;scope:string;preview:boolean}>{
 const saved=(await loadAuthBackends(db,secret)).find(x=>x.id===id);
 if(!saved&&draft===undefined)throw Error('unknown_backend');
 const b=draft===undefined?saved!:await prepareAuthBackend(db,secret,id,draft);
 validateAuthBackend(b.id,b.kind,b.config);
 let scope='configuration';
 if(b.kind==='ldap'){
  const {Client}=await import('ldapts');
  const c=b.config;
  const settings=ldapSettingsFromEnv({LDAP_URL:c.url,LDAP_STARTTLS:c.startTls?'true':'false',LDAP_BIND_DN:c.bindDn,LDAP_BIND_PASSWORD:c.bindPassword,LDAP_BASE_DN:c.baseDn,
   LDAP_USER_FILTER:c.filter,LDAP_ID_ATTRIBUTE:c.idAttribute,LDAP_EMAIL_ATTRIBUTE:c.emailAttribute,LDAP_GROUP_ATTRIBUTE:c.groupAttribute,
   LDAP_ADMIN_GROUP_DN:c.adminGroupDn,LDAP_PRESENTER_GROUP_DN:c.presenterGroupDn,LDAP_ORGANIZATION_ID:c.organizationId,
   LDAP_AUTO_PROVISION:c.autoProvision?'true':'false',LDAP_TLS_CA_FILE:c.caFile,LDAP_LABEL:c.label})!;
  const {readFileSync}=await import('node:fs');
  const tlsOptions={rejectUnauthorized:true,minVersion:'TLSv1.2' as const,...(settings.caFile?{ca:[readFileSync(settings.caFile)]}:{})};
  const client=new Client({url:settings.url,timeout:8000,connectTimeout:5000,tlsOptions});
  try{if(settings.startTls)await client.startTLS(tlsOptions);await client.bind(settings.bindDn,settings.bindPassword);
   await client.search(settings.baseDn,{scope:'base',filter:'(objectClass=*)',attributes:['1.1'],sizeLimit:1,timeLimit:5});scope='secure_ldap_bind_and_base_search';
  }finally{await client.unbind().catch(()=>{})}
 }else if(b.kind==='oidc'){
  const provider={...b.config,id:b.id} as OidcProvider;
  const discovery=validateDiscovery(provider,await fetchOidcJson(provider.issuer.replace(/\/$/,'')+'/.well-known/openid-configuration'));
  const jwks=await fetchOidcJson(discovery.jwks_uri);
  if(!Array.isArray(jwks.keys)||!jwks.keys.length)throw Error('oidc_keys_unavailable');
  scope='oidc_discovery_and_jwks'; // client credentials require an interactive authorization flow
 }else if(b.kind==='social'){
  scope='configuration_only_interactive_oauth_required'; // cannot prove client secret without user authorization
 }else scope='local_internal';
 // A draft test must never update last_tested_at or activate/store the proposed credentials.
 if(draft===undefined)await db.query('UPDATE auth_backends SET last_tested_at=now() WHERE id=$1',[id]);
 return {ok:true,scope,preview:draft!==undefined};
}
