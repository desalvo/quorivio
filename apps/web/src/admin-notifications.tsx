/** RC332: server-wide notification controls, with independent admin audiences per channel. */
import React,{useEffect,useState} from 'react';
type Req=<T=any>(url:string,method?:string,body?:unknown)=>Promise<T>;
type Channel='email'|'pushover'|'telegram'|'whatsapp';
type Event='user_status'|'system_alert'|'debug_session';
type ChannelConfig={enabled:boolean;allAdmins:boolean;adminIds:string[];destinations:Record<string,string>;token:string;tokenConfigured?:boolean;phoneNumberId:string;templateName:string;language:string;apiVersion:string};
type Settings={events:Record<Event,boolean>;channels:Record<Channel,ChannelConfig>;supportEmail:string;notifyUsers:boolean};
type Admin={id:string;email:string};
const keys:Channel[]=['email','pushover','telegram','whatsapp'];
const titles:Record<Channel,string>={email:'E-mail (SMTP)',pushover:'Pushover',telegram:'Telegram Bot',whatsapp:'WhatsApp Cloud API'};
const eventNames:Record<Event,string>={user_status:'Registrazioni e modifiche di stato degli utenti',system_alert:'Errori, warning e alert di sistema',debug_session:'Nuove sessioni inviate per assistenza'};
export function AdminNotificationsPanel({request}:{request:Req}){
 const [cfg,setCfg]=useState<Settings|null>(null),[admins,setAdmins]=useState<Admin[]>([]),[busy,setBusy]=useState(false),[status,setStatus]=useState('');
 const load=async()=>{const response=await request<{settings:Settings;admins:Admin[]}>('/admin/notifications');setCfg(response.settings);setAdmins(response.admins)};
 useEffect(()=>{void load().catch(e=>setStatus(String(e)))},[]);
 const patch=(value:Partial<Settings>)=>setCfg(old=>old?{...old,...value}:old);
 const patchCh=(name:Channel,value:Partial<ChannelConfig>)=>setCfg(old=>old?{...old,channels:{...old.channels,[name]:{...old.channels[name],...value}}}:old);
 const save=async()=>{if(!cfg)return;setBusy(true);setStatus('');
  try{
   const channels=Object.fromEntries(keys.map(name=>{const {tokenConfigured,...rest}=cfg.channels[name];return [name,rest]}));
   const r=await request<{settings:Settings}>('/admin/notifications','PUT',{...cfg,channels});
   setCfg(r.settings);setStatus('Notifiche salvate e applicate a tutte le repliche.');
  }catch(e){setStatus('Salvataggio non riuscito: '+String(e))}finally{setBusy(false)}
 };
 const test=async()=>{setBusy(true);try{const result=await request<{attempted:number;failed:number}>('/admin/notifications/test','POST',{event:'debug_session'});setStatus('Invii tentati: '+result.attempted+' · non riusciti: '+result.failed)}catch(e){setStatus(String(e))}finally{setBusy(false)}};
 return <section className="panel admin-notifications" aria-label="Notifiche del server">
  <h3>Notifiche</h3><p className="muted tiny">I canali sono disabilitati per default; ogni canale può inviare avvisi a tutti gli amministratori o a un elenco selezionato. Le credenziali restano cifrate nel database e non vengono restituite dal server.</p>
  {!cfg?<p>Caricamento configurazione notifiche…</p>:<>
   <h4>Tipi di evento</h4>
   {(Object.keys(eventNames) as Event[]).map(k=><label key={k}><input type="checkbox" checked={cfg.events[k]} onChange={e=>patch({events:{...cfg.events,[k]:e.target.checked}})}/>{eventNames[k]}</label>)}
   <label><input type="checkbox" checked={cfg.notifyUsers} onChange={e=>patch({notifyUsers:e.target.checked})}/>Permetti notifiche anche agli utenti (solo eventi che li riguardano)</label>
   <label>E-mail dell'autore per le segnalazioni (.quo)<input type="email" maxLength={254} value={cfg.supportEmail} onChange={e=>patch({supportEmail:e.target.value})}/></label>
   {keys.map(name=>{
    const ch=cfg.channels[name];
    return <fieldset className="panel" key={name}><legend>{titles[name]}</legend>
     <label><input type="checkbox" checked={ch.enabled} onChange={e=>patchCh(name,{enabled:e.target.checked})}/>Attiva il canale</label>
     <label><input type="checkbox" checked={ch.allAdmins} onChange={e=>patchCh(name,{allAdmins:e.target.checked})}/>Notifica tutti gli amministratori</label>
     {!ch.allAdmins&&<div className="admin-notifications-recipients" role="group" aria-label={'Destinatari '+titles[name]}>{admins.map(admin=><label key={admin.id}><input type="checkbox" checked={ch.adminIds.includes(admin.id)} onChange={e=>patchCh(name,{adminIds:e.target.checked?[...ch.adminIds,admin.id]:ch.adminIds.filter(id=>id!==admin.id)})}/>{admin.email}</label>)}</div>}
     {name!=='email'&&<><label>{name==='pushover'?'Application API token':name==='telegram'?'Bot token':'Meta access token'}<input type="password" autoComplete="new-password" value={ch.token||''} placeholder={ch.tokenConfigured?'Token cifrato salvato — lascia vuoto per conservarlo':'Token obbligatorio per attivare'} onChange={e=>patchCh(name,{token:e.target.value})}/></label>
      {admins.filter(a=>ch.allAdmins||ch.adminIds.includes(a.id)).map(admin=><label key={admin.id}>{admin.email} — {name==='pushover'?'Pushover User Key':name==='telegram'?'Telegram Chat ID':'Numero WhatsApp E.164'}<input value={ch.destinations[admin.id]||''} placeholder={name==='whatsapp'?'+39…':''} onChange={e=>patchCh(name,{destinations:{...ch.destinations,[admin.id]:e.target.value}})}/></label>)}
     </>}
     {name==='whatsapp'&&<><label>Meta Phone Number ID<input value={ch.phoneNumberId||''} onChange={e=>patchCh(name,{phoneNumberId:e.target.value})}/></label><label>Nome template WhatsApp approvato<input value={ch.templateName} onChange={e=>patchCh(name,{templateName:e.target.value})}/></label><label>Codice lingua template<input value={ch.language} onChange={e=>patchCh(name,{language:e.target.value})}/></label><label>Graph API version<input value={ch.apiVersion} onChange={e=>patchCh(name,{apiVersion:e.target.value})}/></label><p className="muted tiny">Il modello di messaggio deve essere approvato da Meta e il destinatario deve avere un opt-in valido.</p></>}
    </fieldset>
   })}
   <div className="downloads"><button type="button" disabled={busy} onClick={()=>void save()}>Salva notifiche</button><button className="outline" type="button" disabled={busy} onClick={()=>void test()}>Invia test sui canali attivi</button></div>
  </>}
  {status&&<p role="status">{status}</p>}
 </section>;
}
