/** Coalesced, per-session live snapshots. A failed database read is reported to
 * callers as well as the logger, so LISTEN/NOTIFY recovery can reconnect and
 * resnapshot instead of treating stale client state as a successful refresh.
 */
export function createLiveSnapshotQueue(readAndSend:(sessionId:string)=>Promise<void>,onError:(error:unknown,sessionId:string)=>void=()=>{}) {
 const pending=new Map<string,{dirty:boolean;promise:Promise<void>}>();
 const enqueue=(sessionId:string):Promise<void>=>{
  const existing=pending.get(sessionId);
  if(existing){existing.dirty=true;return existing.promise}
  const state={dirty:false,promise:Promise.resolve()};
  pending.set(sessionId,state);
  // Defer execution one microtask so the promise is stored before a reentrant
  // enqueue, and never remove a newer generation of the same session.
  state.promise=(async()=>{
   let firstError:unknown;let failed=false;
   try {
    do {
     state.dirty=false;
     try {await readAndSend(sessionId)}
     catch(error){if(!failed){firstError=error;failed=true}try{onError(error,sessionId)}catch{/* logging must not corrupt queue state */}}
    } while(state.dirty);
    if(failed)throw firstError;
   } finally {if(pending.get(sessionId)===state)pending.delete(sessionId)}
  })();
  return state.promise;
 };
 return {enqueue,pendingCount:()=>pending.size};
}
