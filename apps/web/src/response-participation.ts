/** Counts unique connected responders, bounded to 0..100%. */
export function responseParticipationPercent(responded:unknown,connected:unknown):number {
 const safe=(n:unknown)=>typeof n==='number'&&Number.isFinite(n)?Math.max(0,Math.trunc(n)):0;
 const total=safe(connected),answered=Math.min(total,safe(responded));
 return total?Math.max(0,Math.min(100,Math.round(100*answered/total))):0;
}
export function responseParticipationGaugeSize(value:unknown):number {
 return typeof value==='number'&&Number.isFinite(value)?Math.max(20,Math.min(100,Math.round(value))):60;
}
