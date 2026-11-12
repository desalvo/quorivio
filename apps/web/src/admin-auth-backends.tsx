/** Server administrator authentication registry: credentials are write-only.
 * Disable/enable each provider independently; the local backend stays active.
 */
import React,{useEffect,useState} from 'react';
type ApiRequest=<T=any>(url:string,method?:string,body?:unknown,options?:{signal?:AbortSignal;cache?:RequestCache})=>Promise<T>;
type Kind='local'|'ldap'|'oidc'|'social';
type Backend={id:string;kind:Kind;enabled:boolean;mfaEnabled:boolean;configured:boolean;lastTestedAt:string|null;config:Record<string,any>;hasSecret:boolean};
const fields:Record<Kind,Array<{key:string;label:string;secret?:boolean;type?:string}>>={
 local:[],
 ldap:[
  {key:'label',label:'Nome visualizzato alla login'},
  {key:'url',label:'LDAP URI (ldaps:// o ldap:// con StartTLS)'},
  {key:'bindDn',label:'DN account di servizio'},
  {key:'bindPassword',label:'Password account di servizio',secret:true},
  {key:'baseDn',label:'Base DN'},
  {key:'filter',label:'Filtro utente ({login})'},
  {key:'idAttribute',label:'Attributo ID immutabile'},
  {key:'emailAttribute',label:'Attributo email'},
  {key:'groupAttribute',label:'Attributo gruppi'},
  {key:'adminGroupDn',label:'DN gruppo amministratori organizzazione'},
  {key:'presenterGroupDn',label:'DN gruppo presentatori'},
  {key:'organizationId',label:'Organization UUID (per auto-provisioning)'},
  {key:'caFile',label:'CA custom: percorso file nel container'}
 ],
 oidc:[
  {key:'label',label:'Nome visualizzato alla login'},
  {key:'issuer',label:'OIDC Issuer (HTTPS)'},
  {key:'clientId',label:'Client ID'},
  {key:'clientSecret',label:'Client secret',secret:true},
  {key:'redirectUri',label:'Redirect URI HTTPS'}
 ],
 social:[
  {key:'label',label:'Nome visualizzato alla login'},
  {key:'clientId',label:'Client ID'},
  {key:'clientSecret',label:'Client secret',secret:true},
  {key:'redirectUri',label:'Redirect URI HTTPS'}
 ]
};
const initialConfig=(id:string,kind:Kind)=>({
 ...(kind==='ldap'?{label:'LDAP / Active Directory',url:'ldaps://',startTls:false,filter:'(uid={login})',idAttribute:'entryUUID',emailAttribute:'mail',groupAttribute:'memberOf',autoProvision:false}:{ }),
 ...(kind==='oidc'?{label:id.toUpperCase(),issuer:'https://',redirectUri:location.origin+'/api/auth/oidc/'+id+'/callback'}:{}),
 ...(kind==='social'?{label:id==='github'?'GitHub':'Facebook',redirectUri:location.origin+'/api/auth/social/'+id+'/callback'}:{})
});
export function AuthBackendSettingsPanel({request}:{request:ApiRequest}){
 const [items,setItems]=useState<Backend[]>([]),[selected,setSelected]=useState('local'),[drafts,setDrafts]=useState<Record<string,Backend>>({});
 const [newId,setNewId]=useState(''),[busy,setBusy]=useState(false),[message,setMessage]=useState('');
 const refresh=async(resetDrafts=true)=>{const r=await request<{backends:Backend[]}>('/admin/auth/backends','GET',undefined,{cache:'no-store'});setItems(r.backends);if(resetDrafts)setDrafts({})};
 useEffect(()=>{void refresh().catch(e=>setMessage(String(e)))},[]);
 const existing=items.find(x=>x.id===selected);
 const item=drafts[selected]||existing;
 const change=(patch:Partial<Backend>)=>{if(!item)return;setDrafts(old=>({...old,[selected]:{...item,...patch}}))};
 const changeConfig=(key:string,value:string|boolean)=>{if(!item)return;change({config:{...item.config,[key]:value}})};
 const save=async()=>{if(!item)return;setBusy(true);setMessage('');
  try{
   await request('/admin/auth/backends/'+encodeURIComponent(item.id),'PUT',{kind:item.kind,enabled:item.kind==='local'?true:item.enabled,mfaEnabled:item.mfaEnabled,config:item.config});
   setDrafts(previous=>{const next={...previous};delete next[item.id];return next});
   try{await refresh(false);setMessage('Backend salvato. Le modifiche si applicano a tutte le repliche del server.');}
   catch{setMessage('Backend salvato; impossibile aggiornare l’elenco. Ricarica per verificarlo.')}}
  catch(e){setMessage('Salvataggio non riuscito: '+String(e))}finally{setBusy(false)}
 };
 const test=async()=>{if(!item)return;setBusy(true);setMessage('');
  // Probe what is visibly edited, not a previous saved version. Draft tests do
  // not persist secrets, update the last-tested timestamp, or enable providers.
  const preview=Boolean(drafts[selected])||!existing;
  const payload=preview?{kind:item.kind,enabled:item.kind==='local'?true:item.enabled,mfaEnabled:item.mfaEnabled,config:item.config}:{};
  try{const result=await request<{ok:true;scope:string;preview:boolean}>('/admin/auth/backends/'+encodeURIComponent(item.id)+'/test','POST',payload);
   const prefix=result.preview?'Test della bozza riuscito (non salvata). ':'Test del backend salvato riuscito. ';
   const detail=result.scope==='configuration_only_interactive_oauth_required'
    ?'La verifica OAuth è solo statica: ID e segreto richiedono un accesso interattivo.'
    :'Ambito verificato: '+result.scope;
   setMessage(prefix+detail);
   await refresh(false).catch(()=>setMessage(prefix+detail+' Impossibile aggiornare l’elenco.'));}
  catch(e){setMessage('Test non riuscito: '+String(e))}finally{setBusy(false)}
 };
 const add=()=>{const id=newId.trim().toLowerCase();
  if(!/^[a-z][a-z0-9_-]{1,31}$/.test(id)||['local','ldap','github','facebook'].includes(id)||items.some(x=>x.id===id)){setMessage('ID OIDC non valido o già utilizzato.');return}
  setDrafts(old=>({...old,[id]:{id,kind:'oidc',enabled:false,mfaEnabled:false,configured:false,hasSecret:false,lastTestedAt:null,config:initialConfig(id,'oidc')}}));
  setSelected(id);setNewId('');setMessage('Configura il provider e salva; sarà inizialmente disabilitato.');
 };
 return <section className="panel auth-backend-settings" aria-label="Autenticazione e autorizzazione server">
  <h3>Backend di autenticazione e autorizzazione</h3>
  <p className="muted tiny">Solo gli amministratori di piattaforma possono configurare questi backend. LDAP(S), Google, GitHub, Facebook e gli altri provider OIDC sono disabilitati per default; possono essere attivi contemporaneamente. Ogni SSO attiva avrà un pulsante separato alla login.</p>
  <label>Backend<select aria-label="Seleziona backend di autenticazione" value={selected} onChange={e=>{setSelected(e.target.value);setMessage('')}}>
   {items.map(p=><option key={p.id} value={p.id}>{p.id==='local'?'Interno':p.config.label||p.id} — {p.enabled?'attivo':'disabilitato'}</option>)}
   {!items.some(x=>x.id===selected)&&item&&<option value={item.id}>{item.id} — nuovo OIDC</option>}
  </select></label>
  <div className="activity-row"><label>Nuovo provider OIDC<input aria-label="ID nuovo provider OIDC" placeholder="infn" maxLength={32} value={newId} onChange={e=>setNewId(e.target.value)}/></label><button type="button" className="outline small" disabled={busy||!newId.trim()} onClick={add}>Aggiungi SSO</button></div>
  {item&&<>
   <p className="muted tiny">Tipo: {item.kind.toUpperCase()} · {item.configured?'Configurazione salvata completa':'Configurazione salvata incompleta'} · Ultimo test salvato: {item.lastTestedAt?new Date(item.lastTestedAt).toLocaleString('it-IT'):'mai eseguito'}{drafts[selected]?' · Modifiche non salvate':''}</p>
   {item.kind==='local'?<p>Il backend interno non può essere disabilitato: mantiene sempre disponibile l’accesso amministrativo.</p>:
    <label><input type="checkbox" checked={item.enabled} onChange={e=>change({enabled:e.target.checked})}/> Abilita questo backend per login e collegamento identità</label>}
   {item.kind==='local'||item.kind==='ldap'?
    <label><input type="checkbox" checked={item.mfaEnabled} onChange={e=>change({mfaEnabled:e.target.checked})}/> Consenti attivazione MFA (TOTP / email) per questo backend</label>:
    <p className="muted tiny">L'MFA della SSO è gestita dall'Identity Provider. Quorivio non applica un secondo codice dopo la SSO.</p>}
   {item.kind==='ldap'&&<><label><input type="checkbox" checked={item.config.startTls===true} onChange={e=>changeConfig('startTls',e.target.checked)}/> Usa StartTLS con LDAP (obbligatorio se URI ldap://)</label><label><input type="checkbox" checked={item.config.autoProvision===true} onChange={e=>changeConfig('autoProvision',e.target.checked)}/> Richiedi provisioning automatico previa approvazione amministratore</label></>}
   {fields[item.kind].map(f=><label key={f.key}>{f.label}<input
      type={f.secret?'password':f.type||'text'} autoComplete={f.secret?'new-password':'off'}
      maxLength={f.secret?2048:1024} value={f.secret?(drafts[selected]?.config[f.key]??''):item.config[f.key]??''}
      placeholder={f.secret?(item.hasSecret?'Segreto già salvato — lascia vuoto per conservarlo':'Inserisci credenziale'):''}
      onChange={e=>changeConfig(f.key,e.target.value)}/>
     </label>)}
   {item.kind==='ldap'&&<p className="muted tiny">TLS con verifica dei certificati sempre attiva. Per CA private, monta il certificato nel server e specifica il percorso. L'account di servizio viene testato con una bind sicura e una ricerca limitata.</p>}
   {item.kind==='oidc'&&<p className="muted tiny">Callback richiesto: /api/auth/oidc/{item.id}/callback. Il test verifica discovery e chiavi JWKS; la prova completa delle credenziali richiede un login.</p>}
   {item.kind==='social'&&<p className="muted tiny">Callback richiesto: /api/auth/social/{item.id}/callback. Il test statico non può provare il client secret senza un accesso OAuth reale.</p>}
   <div className="downloads"><button type="button" className="primary small" disabled={busy} onClick={()=>void save()}>Salva configurazione</button><button type="button" className="outline small" disabled={busy} onClick={()=>void test()}>{drafts[selected]||!existing?'Testa bozza senza salvare':'Testa backend salvato'}</button><button type="button" className="outline small" disabled={busy} onClick={()=>{if(Object.keys(drafts).length>0&&!window.confirm('Ricaricare? Le modifiche non salvate a tutti i backend andranno perse.'))return;void refresh().catch(e=>setMessage(String(e)))}}>Ricarica</button></div>
  </>}
  {message&&<p role="status">{message}</p>}
 </section>;
}
