/** Per-account, fail-closed rate-limit classes for authenticated presenter UI actions.
 * Anonymous reads and all sensitive writes retain the original 100/min/IP cap.
 * Dedicated keys prevent benign presenter refreshes from exhausting write quotas.
 * The DB still holds every bucket, so independent replicas enforce one budget. */
export type ApiRateClass='presenter-read'|'presenter-navigation'|'default';
export function apiRateClass(method:string,path:string,authenticatedUser:string|null):ApiRateClass{
 if(!authenticatedUser)return 'default';
 if(method==='GET'&&/^\/sessions\//.test(path))return 'presenter-read';
 if(method==='POST'&&/^\/sessions\/[0-9a-f-]{36}\/activities\/[0-9a-f-]{36}\/open$/i.test(path))return 'presenter-navigation';
 return 'default';
}
export function apiRateBudget(kind:ApiRateClass){return kind==='presenter-read'?360:kind==='presenter-navigation'?180:100;}
