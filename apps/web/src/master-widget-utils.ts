/** Session-wide layout: local Title/Footer overrides the corresponding master kind.
 *  Never materialize inherited widgets into the page draft without explicit consent.
 */
export type MasterWidget={id:string;kind:string;position?:{x:number;y:number;width:number;height:number;rotation:number};[key:string]:unknown};
export function normalizeLegacyFooter<W extends {kind:string;position?:{x:number;y:number;width:number;height:number;rotation?:number}}>(w:W):W{
 const p=w.position;
 if(w.kind==='footer'&&p&&p.x===0&&p.y===94&&p.width===100&&p.height===6){
  return {...w,position:{...p,y:87,height:13}};
 }
 return w;
}
export function resolveSlideMasterWidgets<W extends {id:string;kind:string}>(local:readonly W[],master:readonly W[]|undefined):W[]{
 const kinds=new Set(local.map(w=>w.kind));
 const pageIds=new Set(local.map(w=>w.id));
 const source=(master||[]).filter(w=>!pageIds.has(w.id)&&(!['title','footer'].includes(w.kind)||!kinds.has(w.kind)));
 const inheritedIds=new Set(source.map(w=>w.id));
 const inherited=source.map(w=>normalizeLegacyFooter({...w,id:`inherited-${w.id}`.slice(0,48),
    ...((w as any).targetWidgetId&&inheritedIds.has((w as any).targetWidgetId)?{targetWidgetId:`inherited-${(w as any).targetWidgetId}`.slice(0,48)}:{})} as W));
 return [...inherited,...local.map(w=>normalizeLegacyFooter(w))];
}
export function masterWidgetTemplate<T extends {id:string;kind:string}>(widgets:readonly T[]):T[]{
 return widgets.filter((w,index,all)=>['title','footer'].includes(w.kind)?all.findIndex(v=>v.kind===w.kind)===index:all.findIndex(v=>v.id===w.id)===index).slice(0,16);
}
