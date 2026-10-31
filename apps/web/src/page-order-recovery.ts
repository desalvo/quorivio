/** Reconcile a page reorder against the authoritative session after an ambiguous HTTP response.
 * A lost PUT response does NOT prove that the server kept the previous order.
 */
export type PageOrderOutcome<T>={snapshot:T;state:'saved'|'recovered'|'rejected'|'concurrent'};

export async function commitAndReconcilePageOrder<T>(
  requested:readonly string[],
  write:()=>Promise<unknown>,
  read:()=>Promise<T>,
  getIds:(snapshot:T)=>readonly string[],
):Promise<PageOrderOutcome<T>>{
  if(!Array.isArray(requested)||requested.length===0||requested.some(id=>typeof id!=='string'||!id)||new Set(requested).size!==requested.length)
    throw new Error('Invalid requested page sequence');
  let writeFailed=false;
  try{await write()}catch{writeFailed=true}
  // Always GET the canonical order, including when PUT failed or its response got lost.
  // Never repeat a possibly committed write: a second PUT could undo concurrent changes.
  const snapshot=await read();
  const actual=getIds(snapshot);
  if(!Array.isArray(actual)||actual.length!==requested.length||actual.some(id=>typeof id!=='string'||!id)||new Set(actual).size!==actual.length)
    throw new Error('Unable to reconcile authoritative page order');
  const expected=new Set(requested);
  if(actual.some(id=>!expected.has(id)))throw new Error('Page collection changed during reorder');
  const equal=actual.every((id,i)=>id===requested[i]);
  return {snapshot,state:equal?(writeFailed?'recovered':'saved'):(writeFailed?'rejected':'concurrent')};
}
