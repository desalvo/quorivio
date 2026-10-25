/** Lossless three-way rebase for collaborative page drafts.
 * The server remains authoritative: applying a rebase never writes to the API.
 * A subsequent save must still use the server's design_revision CAS.
 */
import type {EditablePageDraft} from './page-draft';

export type MergeChoice='local'|'remote';
export type MergeConflict={path:string;label:string;local:unknown;remote:unknown};
export type MergeResult={draft:EditablePageDraft;conflicts:MergeConflict[]};
const MISSING=Symbol('missing');
type Node=unknown|typeof MISSING;
const isRecord=(v:Node):v is Record<string,unknown>=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const forbidden=new Set(['__proto__','constructor','prototype']);
const pointer=(s:string)=>s.replace(/~/g,'~0').replace(/\//g,'~1');
const canonical=(v:Node):string=>{
 if(v===MISSING)return 'missing';
 if(Array.isArray(v))return '['+v.map(canonical).join(',')+']';
 if(isRecord(v))return '{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';
 return JSON.stringify(v)??'undefined';
};
const same=(a:Node,b:Node)=>canonical(a)===canonical(b);
function copy(v:Node):Node{
 if(v===MISSING)return MISSING;
 if(Array.isArray(v))return v.map(x=>copy(x));
 if(isRecord(v)){const out:Record<string,unknown>=Object.create(null);for(const k of Object.keys(v)){if(forbidden.has(k))throw Error('unsafe_draft_key');out[k]=copy(v[k]);}return out;}
 return v;
}
function validateWidgets(d:EditablePageDraft):void{
 if(!Array.isArray(d.widgets)||d.widgets.length>500)throw Error('invalid_merge_widgets');
 const ids=new Set<string>();
 for(const w of d.widgets){if(!isRecord(w)||typeof w.id!=='string'||!w.id||w.id.length>128||ids.has(w.id)||forbidden.has(w.id))throw Error('invalid_merge_widget_ids');ids.add(w.id);}
}
export function mergePageDrafts(base:EditablePageDraft,local:EditablePageDraft,remote:EditablePageDraft,choices:Readonly<Record<string,MergeChoice>>={}):MergeResult{
 for(const d of [base,local,remote])validateWidgets(d);
 const conflicts:MergeConflict[]=[];
 const choose=(path:string,label:string,b:Node,l:Node,r:Node):Node=>{
  conflicts.push({path,label,local:l===MISSING?undefined:copy(l),remote:r===MISSING?undefined:copy(r)});
  return copy(choices[path]==='local'?l:r);
 };
 const value=(path:string,label:string,b:Node,l:Node,r:Node,depth=0):Node=>{
  if(same(l,r))return copy(l);
  if(same(l,b))return copy(r);
  if(same(r,b))return copy(l);
  if(depth<12&&isRecord(l)&&isRecord(r)&&(isRecord(b)||b===MISSING)){
   const obj:Record<string,unknown>=Object.create(null);
   const keys=new Set([...Object.keys(isRecord(b)?b:{}),...Object.keys(l),...Object.keys(r)]);
   for(const k of keys){if(forbidden.has(k))throw Error('unsafe_draft_key');
    const part=value(path+'/'+pointer(k),label+' · '+k,isRecord(b)&&Object.hasOwn(b,k)?b[k]:MISSING,Object.hasOwn(l,k)?l[k]:MISSING,Object.hasOwn(r,k)?r[k]:MISSING,depth+1);
    if(part!==MISSING)obj[k]=part;
   }
   return obj;
  }
  return choose(path,label,b,l,r);
 };
 const bmap=new Map(base.widgets.map(w=>[(w as {id:string}).id,w]));
 const lmap=new Map(local.widgets.map(w=>[(w as {id:string}).id,w]));
 const rmap=new Map(remote.widgets.map(w=>[(w as {id:string}).id,w]));
 const merged=new Map<string,unknown>();
 for(const id of new Set([...bmap.keys(),...lmap.keys(),...rmap.keys()])){
  const baseWidget=bmap.has(id)?bmap.get(id):MISSING;
  const localWidget=lmap.has(id)?lmap.get(id):MISSING;
  const remoteWidget=rmap.has(id)?rmap.get(id):MISSING;
  // Concurrent insertion with an identical identifier is not a field-level edit.
  const w=baseWidget===MISSING&&localWidget!==MISSING&&remoteWidget!==MISSING&&!same(localWidget,remoteWidget)
   ?choose('/widgets/'+pointer(id),'Widget '+id,baseWidget,localWidget,remoteWidget)
   :value('/widgets/'+pointer(id),'Widget '+id,baseWidget,localWidget,remoteWidget);
  if(w!==MISSING)merged.set(id,w);
 }
 const ids=(d:EditablePageDraft)=>d.widgets.map(w=>(w as {id:string}).id);
 const baseIds=ids(base),localIds=ids(local),remoteIds=ids(remote);
 const baseSet=new Set(baseIds);
 const reordered=(arr:string[])=>{
  const common=arr.filter(id=>baseSet.has(id));
  return !same(common,baseIds.filter(id=>common.includes(id)));
 };
 const lReordered=reordered(localIds),rReordered=reordered(remoteIds);
 let preferred:string[];
 if(lReordered&&rReordered&&!same(localIds.filter(id=>baseSet.has(id)&&rmap.has(id)),remoteIds.filter(id=>baseSet.has(id)&&lmap.has(id)))){
  const orderPath='/@widget-order';
  choose(orderPath,'Ordine dei widget',baseIds,localIds,remoteIds);
  preferred=choices[orderPath]==='local'?localIds:remoteIds;
 }else preferred=lReordered&&!rReordered?localIds:remoteIds;
 const ordered=[...new Set([...preferred,...(preferred===localIds?remoteIds:localIds),...baseIds])].filter(id=>merged.has(id));
 const out:Record<string,unknown>=Object.create(null);
 const fields:(keyof EditablePageDraft)[]=['questionHeader','resultHeader','questionBackground','resultBackground','questionBackgroundColor','resultBackgroundColor','questionBackgroundAsset','resultBackgroundAsset'];
 for(const field of fields)out[field]=value('/'+field,field,base[field],local[field],remote[field]);
 out.widgets=ordered.map(id=>merged.get(id));
 return {draft:out as EditablePageDraft,conflicts};
}
