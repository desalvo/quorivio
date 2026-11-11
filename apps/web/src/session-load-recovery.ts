/** Restore a session without trusting old browser route state or a WebSocket payload.
 * Invalid snapshots and expired credentials must never blank the React root. */
export type SessionFailure='expired'|'unavailable'|'retry';
export function sessionFailureForStatus(status:number|undefined):SessionFailure{
 if(status===401)return 'expired';
 if(status===403||status===404||status===410)return 'unavailable';
 return 'retry';
}
export function isOwnerSessionSnapshot(value:unknown,sessionId:string):boolean{
 if(!value||typeof value!=='object')return false;
 const x=value as Record<string,any>;
 if(!x.session||typeof x.session!=='object'||x.session.id!==sessionId||typeof x.session.title!=='string')return false;
 if(!Array.isArray(x.activities)|| (x.results!==undefined&&!Array.isArray(x.results)) || (x.totals!==undefined&&!Array.isArray(x.totals)))return false;
 return x.activities.every(a=>a&&typeof a==='object'&&typeof a.id==='string');
}

/** Browser fixtures and older server responses may omit optional statistic arrays.
 * Normalize them before rendering so the dashboard never crashes on missing fields. */
/** Audience and presenter pages share a transport, not a render lifecycle.
 * A damaged audience-only page or obsolete per-page shape must not invalidate
 * the authenticated presenter workspace or silently reset session selection.
 * This is an in-memory defensive view; it never rewrites stored page designs. */
export function normalizeOwnerSessionSnapshot<T extends {results?:unknown;totals?:unknown}>(value:T):T&{results:any[];totals:any[]}{
 const input=value as T&{activities?:unknown;session?:unknown};
 const rawPages=Array.isArray(input.activities)?input.activities:[];
 const validPageIds=new Set(rawPages.filter((page:any)=>page&&typeof page.id==='string').map((page:any)=>page.id));
 const normalizeDesign=(design:any)=>{
  if(design==null)return design;
  if(typeof design!=='object'||Array.isArray(design))return {};
  const widgets=Array.isArray(design.widgets)?design.widgets.filter((widget:any)=>widget&&typeof widget==='object'&&!Array.isArray(widget)):[];
  const mapping=design.audiencePageId;
  return {...design,widgets,...(typeof mapping==='string'&&mapping&&!validPageIds.has(mapping)?{audiencePageId:undefined}:{})};
 };
 const pages=rawPages.map((page:any)=>({
  ...page,
  page_design:normalizeDesign(page.page_design),
  result_design:normalizeDesign(page.result_design),
  options:Array.isArray(page.options)?page.options.filter((option:any)=>option&&typeof option==='object'):[],
 }));
 return {...value,...(Array.isArray(input.activities)?{activities:pages}:{}),results:Array.isArray(value.results)?value.results:[],totals:Array.isArray(value.totals)?value.totals:[]} as T&{results:any[];totals:any[]};
}
