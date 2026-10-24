/** Stable layer operations: selected widgets move as a contiguous group without changing their internal order. */
type LayerItem={id:string};
export type LayerAction='front'|'back'|'forward'|'backward';
export function reorderWidgetLayers<T extends LayerItem>(widgets:readonly T[],ids:readonly string[],action:LayerAction):T[]{
 const chosen=new Set(ids);
 if(!chosen.size||!widgets.some(w=>chosen.has(w.id)))return widgets as T[];
 const before=widgets.slice();
 let after:T[];
 if(action==='front'||action==='back'){
  const selected=before.filter(w=>chosen.has(w.id)),others=before.filter(w=>!chosen.has(w.id));
  after=action==='front'?[...others,...selected]:[...selected,...others];
 }else{
  after=[...before];
  // Swap adjacent selected/unselected boundaries once; preserves selected relative order.
  if(action==='forward'){
   for(let i=after.length-2;i>=0;i--)if(chosen.has(after[i].id)&&!chosen.has(after[i+1].id)){
    [after[i],after[i+1]]=[after[i+1],after[i]];
   }
  }else if(action==='backward'){
   for(let i=1;i<after.length;i++)if(chosen.has(after[i].id)&&!chosen.has(after[i-1].id)){
    [after[i],after[i-1]]=[after[i-1],after[i]];
   }
  }else throw new Error('Unsupported layer action');
 }
 return after.every((w,i)=>w===before[i])?widgets as T[]:after;
}
