/** Remove references to a deleted session page while preserving unrelated design data.
 * Called under the session row lock; no dangling cross-page audience/result ids. */
export function unlinkDeletedPage(design:unknown,deletedId:string):{design:unknown;changed:boolean}{
 if(!design||typeof design!=='object'||Array.isArray(design))return {design,changed:false};
 const old=design as Record<string,unknown>;
 let changed=false;
 const copy:Record<string,unknown>={...old};
 if(copy.audiencePageId===deletedId){delete copy.audiencePageId;changed=true;}
 if(Array.isArray(old.widgets)){
  copy.widgets=old.widgets.map((raw:unknown)=>{
   if(!raw||typeof raw!=='object'||Array.isArray(raw))return raw;
   const w=raw as Record<string,unknown>;
   if(w.kind!=='results-button'||w.targetActivityId!==deletedId)return raw;
   const cleared={...w};
   delete cleared.targetActivityId;delete cleared.targetWidgetId;delete cleared.targetQuestionId;
   changed=true;return cleared;
  });
 }
 return {design:changed?copy:design,changed};
}
