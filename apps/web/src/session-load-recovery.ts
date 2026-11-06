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
export function normalizeOwnerSessionSnapshot<T extends {results?:unknown;totals?:unknown}>(value:T):T&{results:any[];totals:any[]}{
 return {...value,results:Array.isArray(value.results)?value.results:[],totals:Array.isArray(value.totals)?value.totals:[]};
}
