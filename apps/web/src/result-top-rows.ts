/** Stable top-N view. Never mutate live input; tie counts retain source order. */
export function topResultRows<T extends {count:number}>(rows:readonly T[],requested?:number):T[]{
 const n=Number.isInteger(requested)&&requested!>=1&&requested!<=20?requested!:5;
 return rows.map((value,index)=>({value,index})).sort((a,b)=>b.value.count-a.value.count||a.index-b.index).slice(0,n).map(item=>item.value);
}
/** Keep the final word and its count together without disabling wrapping elsewhere. */
export function splitResultLabel(value:string):{prefix:string;last:string}{
 const parts=/^(.*\s)(\S+)$/s.exec(value);
 return parts?{prefix:parts[1],last:parts[2]}:{prefix:'',last:value};
}

/** Results bars use a stable author-selected sort, preserving original order on ties. */
export const RESULT_BAR_ORDERS=['index-asc','index-desc','count-asc','count-desc'] as const;
export type ResultBarOrder=typeof RESULT_BAR_ORDERS[number];
export function sortedResultBars<T extends {count:number}>(rows:readonly T[],order:unknown):T[]{
 const mode=RESULT_BAR_ORDERS.includes(order as ResultBarOrder)?order as ResultBarOrder:'count-desc';
 return rows.map((value,index)=>({value,index})).sort((a,b)=>{
  if(mode==='index-asc')return a.index-b.index;
  if(mode==='index-desc')return b.index-a.index;
  const ac=Number.isFinite(a.value.count)?Math.max(0,a.value.count):0;
  const bc=Number.isFinite(b.value.count)?Math.max(0,b.value.count):0;
  return (mode==='count-asc'?ac-bc:bc-ac)||a.index-b.index;
 }).map(x=>x.value);
}
/** The maximum visible answer fills 100% of the available horizontal track. */
export function resultBarWidth(count:number,maximum:number):number {
 if(!Number.isFinite(count)||!Number.isFinite(maximum)||count<=0||maximum<=0)return 0;
 return Math.min(100,Math.max(0,100*count/maximum));
}

/** Apply the author's sort BEFORE selecting the visible top-N bars.
 * Calling topResultRows here would silently override index/ascending order. */
export function visibleResultBars<T extends {count:number}>(rows:readonly T[],order:unknown,requested?:number):T[]{
 const limit=Number.isInteger(requested)&&requested!>=1&&requested!<=20?requested!:5;
 return sortedResultBars(rows,order).slice(0,limit);
}
