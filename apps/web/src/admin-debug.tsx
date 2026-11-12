/** RC332 administrator-only diagnostic archive listing. */
import React,{useEffect,useState} from 'react';
type Req=<T=any>(url:string,method?:string,body?:unknown)=>Promise<T>;
type Item={id:string;session_id:string;kind:'bug'|'feature';message:string;sender:string;created_at:string;expires_at:string;email_delivery_status:string;consent_diagnostics:boolean};
export function AdminDebugPanel({request}:{request:Req}){
 const [items,setItems]=useState<Item[]>([]),[retention,setRetention]=useState(30),[message,setMessage]=useState('');
 const refresh=async()=>{const r=await request<{items:Item[];retentionDays:number}>('/admin/debug-submissions');setItems(r.items);setRetention(r.retentionDays)};
 useEffect(()=>{void refresh().catch(e=>setMessage(String(e)))},[]);
 return <section className="panel admin-debug" aria-label="Sessioni ricevute per debug">
  <h3>Debug — sessioni inviate dagli utenti</h3>
  <p className="muted tiny">Archivi .quo visibili soltanto agli amministratori. Durata {retention} giorni dalla ricezione (modificabile in Generale); pulizia automatica anche se l'invio delle notifiche fallisce. Eventuali diagnostiche sono incluse solo con consenso esplicito.</p>
  <button type="button" className="outline small" onClick={()=>void refresh().catch(e=>setMessage(String(e)))}>Aggiorna elenco</button>
  {items.length===0?<p>Nessuna sessione di debug conservata.</p>:<div style={{overflowX:'auto'}}><table><thead><tr><th>Data</th><th>Mittente</th><th>Tipo</th><th>Segnalazione</th><th>Mail autore</th><th>Scadenza</th><th>Download</th></tr></thead><tbody>{items.map(item=><tr key={item.id}><td>{new Date(item.created_at).toLocaleString('it-IT')}</td><td>{item.sender}</td><td>{item.kind}</td><td>{item.message}</td><td>{item.email_delivery_status}</td><td>{new Date(item.expires_at).toLocaleDateString('it-IT')}</td><td><a href={'/api/admin/debug-submissions/'+encodeURIComponent(item.id)+'/download'} download>Scarica .quo</a></td></tr>)}</tbody></table></div>}
  {message&&<p role="status">{message}</p>}
 </section>;
}
