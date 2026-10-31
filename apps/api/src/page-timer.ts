/** All interactive participant mutations on an open page share the shortest timer deadline. */
export function livePageTimerSeconds(design:unknown):number|undefined{
 const widgets=(design as {widgets?:unknown})?.widgets;
 if(!Array.isArray(widgets))return undefined;
 const durations=widgets.filter(w=>w?.kind==='timer')
  .map(w=>w.durationSeconds??60)
  .filter(s=>Number.isInteger(s)&&s>=1&&s<=3600) as number[];
 return durations.length?Math.min(...durations):undefined;
}
export function livePageTimerExpired(design:unknown,openedAt:string|Date|null|undefined,databaseNow:string|Date):boolean{
 const seconds=livePageTimerSeconds(design);
 if(seconds===undefined)return false;
 const start=openedAt?new Date(openedAt).getTime():NaN;
 const current=new Date(databaseNow).getTime();
 // Fail closed when a timer is configured but the page has not begun.
 return !Number.isFinite(start)||!Number.isFinite(current)||current>=start+seconds*1000;
}
