/** Canonical live QR display state, without persisting access tokens on the client.
 * A new session/revision hides any previous QR immediately; a failed lookup
 * never leaves an old scannable symbol on screen. */
export type SyncedQrTarget={sourceKey:string;url:string;revision:number;failed:boolean};
export const EMPTY_QR_TARGET:SyncedQrTarget={sourceKey:'',url:'',revision:0,failed:false};

export function visibleQrTarget(state:SyncedQrTarget,sourceKey:string):SyncedQrTarget|null{
 return state.sourceKey===sourceKey?state:null;
}

export function updateQrTarget(state:SyncedQrTarget,sourceKey:string,url:string|null):SyncedQrTarget{
 const current=visibleQrTarget(state,sourceKey)??{...EMPTY_QR_TARGET,sourceKey};
 if(url===null){
  if(current.failed&&!current.url)return current;
  return {...current,url:'',revision:current.url?current.revision+1:current.revision,failed:true};
 }
 if(current.url===url&&!current.failed)return current;
 return {...current,url,revision:current.revision+1,failed:false};
}
