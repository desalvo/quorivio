/** Disposable rehearsal timer. Time starts when the preview page is entered,
 * never from a published session's historical opened_at timestamp. Presenter's
 * and participant's panes share one deadline and switching panes cannot reset it. */
export function rehearsalDurationSeconds(widgetSeconds:unknown, pageSeconds:unknown):number{
 const selected=[widgetSeconds,pageSeconds].find(v=>typeof v==='number'&&Number.isFinite(v)&&Number.isInteger(v)&&v>=1&&v<=3600);
 return typeof selected==='number'?selected:30;
}
export function rehearsalExpired(startedAt:number,durationSeconds:number,now:number):boolean{
 return Number.isFinite(startedAt)&&Number.isFinite(now)&&Number.isInteger(durationSeconds)&&durationSeconds>0 && now>=startedAt+durationSeconds*1000;
}
/** An already submitted answer is immutable even if the deadline expires. */
export function maySubmitTimedRehearsal(startedAt:number,seconds:number,now:number,sent:boolean):boolean{
 return !sent&&!rehearsalExpired(startedAt,seconds,now);
}
