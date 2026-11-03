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
