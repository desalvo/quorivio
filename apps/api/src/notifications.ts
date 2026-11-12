/** RC332: opt-in multichannel notices, encrypted at rest. The public API never reveals tokens. */
import type {Pool} from 'pg';
import type {SmtpConfig} from './smtp.js';
import {sealAuthConfig,openAuthConfig} from './auth-backends.js';

export type NoticeEvent='user_status'|'system_alert'|'debug_session';
export type NoticeChannel='email'|'pushover'|'telegram'|'whatsapp';
type ChannelConfig={enabled:boolean;allAdmins:boolean;adminIds:string[];destinations:Record<string,string>;token:string;phoneNumberId:string;templateName:string;language:string;apiVersion:string};
export type NoticeConfig={events:Record<NoticeEvent,boolean>;channels:Record<NoticeChannel,ChannelConfig>;supportEmail:string;notifyUsers:boolean};
const channels:NoticeChannel[]=['email','pushover','telegram','whatsapp'];
const events:NoticeEvent[]=['user_status','system_alert','debug_session'];
const uuid=/^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i;
const email=/^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const blank=():ChannelConfig=>({enabled:false,allAdmins:true,adminIds:[],destinations:{},token:'',phoneNumberId:'',templateName:'quorivio_alert',language:'it',apiVersion:'v23.0'});
export const defaultNoticeConfig=():NoticeConfig=>({events:{user_status:true,system_alert:true,debug_session:true},channels:{email:blank(),pushover:blank(),telegram:blank(),whatsapp:blank()},supportEmail:'braket71@gmail.com',notifyUsers:false});
export function mergeNoticeConfig(input:unknown,previous:NoticeConfig):NoticeConfig{
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('invalid_notification_settings');
 const patch=input as Record<string,any>,next=structuredClone(previous);
 for(const key of Object.keys(patch))if(!['events','channels','supportEmail','notifyUsers'].includes(key))throw Error('invalid_notification_field');
 if(patch.supportEmail!==undefined){if(typeof patch.supportEmail!=='string'||!email.test(patch.supportEmail)||patch.supportEmail.length>254)throw Error('invalid_support_email');next.supportEmail=patch.supportEmail.toLowerCase()}
 if(patch.notifyUsers!==undefined){if(typeof patch.notifyUsers!=='boolean')throw Error('invalid_notify_users');next.notifyUsers=patch.notifyUsers}
 if(patch.events!==undefined){
  if(!patch.events||typeof patch.events!=='object'||Array.isArray(patch.events))throw Error('invalid_notification_events');
  for(const [e,value] of Object.entries(patch.events)){if(!events.includes(e as NoticeEvent)||typeof value!=='boolean')throw Error('invalid_notification_event');next.events[e as NoticeEvent]=value}
 }
 if(patch.channels!==undefined){
  if(!patch.channels||typeof patch.channels!=='object'||Array.isArray(patch.channels))throw Error('invalid_notification_channels');
  for(const [name,raw] of Object.entries(patch.channels)){
   if(!channels.includes(name as NoticeChannel)||!raw||typeof raw!=='object'||Array.isArray(raw))throw Error('invalid_notification_channel');
   const c=raw as Record<string,any>,target=next.channels[name as NoticeChannel];
   for(const key of Object.keys(c))if(!['enabled','allAdmins','adminIds','destinations','token','phoneNumberId','templateName','language','apiVersion'].includes(key))throw Error('invalid_notification_channel_field');
   if(c.enabled!==undefined){if(typeof c.enabled!=='boolean')throw Error('invalid_notification_enabled');target.enabled=c.enabled}
   if(c.allAdmins!==undefined){if(typeof c.allAdmins!=='boolean')throw Error('invalid_notification_admin_mode');target.allAdmins=c.allAdmins}
   if(c.adminIds!==undefined){if(!Array.isArray(c.adminIds)||c.adminIds.length>100||c.adminIds.some((id:any)=>typeof id!=='string'||!uuid.test(id)))throw Error('invalid_notification_recipients');target.adminIds=[...new Set(c.adminIds)]}
   if(c.destinations!==undefined){
    if(!c.destinations||typeof c.destinations!=='object'||Array.isArray(c.destinations)||Object.keys(c.destinations).length>100)throw Error('invalid_notification_destinations');
    target.destinations={};
    for(const [id,value] of Object.entries(c.destinations)){if(!uuid.test(id)||typeof value!=='string'||value.length>120||/[\x00-\x1f]/.test(value))throw Error('invalid_notification_destination');if(value)target.destinations[id]=value}
   }
   for(const field of ['token','phoneNumberId','templateName','language','apiVersion'] as const)if(c[field]!==undefined){
    if(typeof c[field]!=='string'||c[field].length>512||/[\x00-\x1f]/.test(c[field]))throw Error('invalid_notification_credential');
    if(field==='token'&&!c[field])continue;
    (target as any)[field]=c[field];
   }
   if(target.enabled&&name==='pushover'&&!/^[A-Za-z0-9]{20,80}$/.test(target.token))throw Error('pushover_token_required');
   if(target.enabled&&name==='telegram'&&!/^[0-9]+:[A-Za-z0-9_-]{25,}$/.test(target.token))throw Error('telegram_token_required');
   if(target.enabled&&name==='whatsapp'&&(!target.token||!/^\d{6,30}$/.test(target.phoneNumberId)||!/^[a-zA-Z0-9_]{1,80}$/.test(target.templateName)||!/^v\d{1,2}\.0$/.test(target.apiVersion)))throw Error('whatsapp_config_required');
  }
 }
 return next;
}
export function publicNoticeConfig(config:NoticeConfig){
 return {...config,channels:Object.fromEntries(channels.map(name=>[name,{...config.channels[name],token:'',tokenConfigured:Boolean(config.channels[name].token)}]))};
}
export async function loadNoticeConfig(db:Pool,secret:string):Promise<NoticeConfig>{
 const r=await db.query('SELECT encrypted_config FROM notification_configuration WHERE id=1');
 if(!r.rowCount||!r.rows[0].encrypted_config)return defaultNoticeConfig();
 return mergeNoticeConfig(openAuthConfig(r.rows[0].encrypted_config,secret),defaultNoticeConfig());
}
export async function saveNoticeConfig(db:Pool,secret:string,input:unknown){
 const next=mergeNoticeConfig(input,await loadNoticeConfig(db,secret));
 const ids=[...new Set(channels.flatMap(c=>next.channels[c].adminIds))];
 if(ids.length){const r=await db.query("SELECT id FROM users WHERE id=ANY($1::uuid[]) AND role='platform_admin' AND approved=true",[ids]);if(r.rows.length!==ids.length)throw Error('invalid_notification_recipients')}
 await db.query('INSERT INTO notification_configuration(id,encrypted_config) VALUES(1,$1) ON CONFLICT(id) DO UPDATE SET encrypted_config=$1,updated_at=now()',[sealAuthConfig(next,secret)]);
 return publicNoticeConfig(next);
}
async function providerRequest(url:string,init:RequestInit){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
 try{const res=await fetch(url,{...init,signal:controller.signal});if(!res.ok)throw Error('notification_provider_failed')}
 finally{clearTimeout(timer)}
}
export async function deliverNotice(db:Pool,secret:string,smtp:SmtpConfig|null,event:NoticeEvent,details:string){
 const config=await loadNoticeConfig(db,secret);if(!config.events[event])return {attempted:0,failed:0};
 const admins=(await db.query("SELECT id,email FROM users WHERE role='platform_admin' AND approved=true ORDER BY email LIMIT 100")).rows as {id:string;email:string}[];
 const message='[Quorivio] '+event.replace(/_/g,' ')+': '+details.replace(/[\x00-\x1f]/g,' ').slice(0,250);
 let attempted=0,failed=0;
 for(const name of channels){
  const ch=config.channels[name];if(!ch.enabled)continue;
  const recipients=admins.filter(a=>ch.allAdmins||ch.adminIds.includes(a.id));if(!recipients.length)continue;
  if(name==='email'){
   if(!smtp){failed++;continue}
   attempted++;
   const {default:mailer}=await import('nodemailer');
   const tx=mailer.createTransport({host:smtp.host,port:smtp.port,secure:smtp.secure,requireTLS:!smtp.secure,auth:{user:smtp.user,pass:smtp.password},connectionTimeout:10000,greetingTimeout:10000,socketTimeout:15000,tls:{rejectUnauthorized:true}});
   try{await tx.sendMail({from:smtp.senderName?{name:smtp.senderName,address:smtp.from}:smtp.from,to:recipients.map(x=>x.email),subject:'[Quorivio] '+event.replace(/_/g,' '),text:message})}
   catch{failed++}finally{tx.close()}
   continue;
  }
  for(const admin of recipients){
   const dest=ch.destinations[admin.id];if(!dest){failed++;continue}attempted++;
   try{
    if(name==='pushover'){
     if(!/^[A-Za-z0-9]{20,80}$/.test(dest))throw Error('invalid_pushover_user');
     await providerRequest('https://api.pushover.net/1/messages.json',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({token:ch.token,user:dest,title:'Quorivio',message}).toString()});
    }else if(name==='telegram'){
     if(!/^-?\d{3,20}$/.test(dest))throw Error('invalid_telegram_chat');
     await providerRequest('https://api.telegram.org/bot'+ch.token+'/sendMessage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chat_id:dest,text:message})});
    }else{
     if(!/^\+[1-9]\d{7,14}$/.test(dest))throw Error('invalid_whatsapp_phone');
     await providerRequest('https://graph.facebook.com/'+ch.apiVersion+'/'+ch.phoneNumberId+'/messages',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+ch.token},body:JSON.stringify({messaging_product:'whatsapp',to:dest.slice(1),type:'template',template:{name:ch.templateName,language:{code:ch.language}}})});
    }
   }catch{failed++}
  }
 }
 return {attempted,failed};
}
export async function sendDebugEmail(smtp:SmtpConfig|null,to:string,id:string,bundle:Buffer,message:string,diagnostics:unknown){
 if(!smtp)return {sent:false,reason:'smtp_not_configured'};
 if(bundle.length>14*1024*1024)return {sent:false,reason:'attachment_too_large'};
 const {default:mailer}=await import('nodemailer');
 const tx=mailer.createTransport({host:smtp.host,port:smtp.port,secure:smtp.secure,requireTLS:!smtp.secure,auth:{user:smtp.user,pass:smtp.password},connectionTimeout:10000,greetingTimeout:10000,socketTimeout:30000,tls:{rejectUnauthorized:true}});
 try{
  await tx.sendMail({from:smtp.senderName?{name:smtp.senderName,address:smtp.from}:smtp.from,to,subject:'[Quorivio] Sessione per debug '+id.slice(0,8),text:message.slice(0,2000),attachments:[
   {filename:'quorivio-'+id+'.quo',content:bundle,contentType:'application/octet-stream'},
   ...(diagnostics?[{filename:'debug-24h.json',content:Buffer.from(JSON.stringify(diagnostics)),contentType:'application/json'}]:[])
  ]});
  return {sent:true,reason:null};
 }catch{return {sent:false,reason:'smtp_delivery_failed'}}finally{tx.close()}
}
