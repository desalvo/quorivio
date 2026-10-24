/** PostgreSQL LISTEN/NOTIFY fan-out between independently running API replicas.
 * Notification payloads contain only UUIDs; snapshots are always read from DB.
 */
export const SESSION_CHANNEL = 'quorivio_session_update';
export function validSessionNotification(payload: unknown): payload is string {
 return typeof payload === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(payload);
}
export type ListenerClient = {
 on(event: 'notification', listener: (msg: {channel:string;payload?:string}) => void): unknown;
 on(event: 'error' | 'end', listener: (...args: any[]) => void): unknown;
 query(sql: string): Promise<unknown>;
 end(): Promise<unknown>;
};
/** Reconnect with exponential backoff. The caller owns the process lifecycle. */
export function startSessionBus(connect: () => Promise<ListenerClient>, onUpdate: (sessionId:string)=>Promise<void>, log: (message:string)=>void = console.error, onReady: ()=>Promise<void> = async()=>{}) {
 let stopped=false, client:ListenerClient|null=null, retry:ReturnType<typeof setTimeout>|null=null, attempt=0;
 const attach=async()=>{
  if(stopped)return;
  try {
   const next=await connect();
   if(stopped){await next.end();return}
   client=next;
   let disconnected=false;
   const failed=()=>{
    if(disconnected||stopped)return;
    disconnected=true;client=null;
    void next.end().catch(()=>{});
    const wait=Math.min(30000,500*Math.pow(2,Math.min(attempt++,6)));
    log('session notification listener disconnected; reconnecting');
    retry=setTimeout(()=>{void attach()},wait);retry.unref?.();
   };
   next.on('notification',msg=>{
    if(!stopped && !disconnected && client===next && msg.channel===SESSION_CHANNEL && validSessionNotification(msg.payload))void onUpdate(msg.payload).catch(()=>{log('session notification update failed; reconnecting');failed()});
   });
   next.on('error',failed);next.on('end',failed);
   await next.query(`LISTEN ${SESSION_CHANNEL}`);
   if(stopped || disconnected || client!==next)return;
   attempt=0;
   // LISTEN does not replay notifications missed while disconnected.
   // Resnapshot every locally connected session after subscribing; any concurrent
   // notification is still delivered by PostgreSQL after LISTEN completes.
   try {await onReady()} catch {log('session notification resynchronization failed; reconnecting');failed()}
  }catch{if(client){await client.end().catch(()=>{});client=null}if(!stopped){const wait=Math.min(30000,500*Math.pow(2,Math.min(attempt++,6)));log('session notification listener unavailable; retrying');retry=setTimeout(()=>{void attach()},wait);retry.unref?.()}}
 };
 void attach();
 return async()=>{stopped=true;if(retry)clearTimeout(retry);if(client)await client.end().catch(()=>{})};
}
