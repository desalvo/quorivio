/** Database-clock deadline policy shared by legacy activities and timed widgets.
 * All replicas must use the same authoritative clock, not their host clocks. */
export function timedDeadline(openedAt:Date|string|null|undefined, durationSeconds:number, databaseNow:Date|string):{valid:boolean;elapsedMs:number}{
 const start=openedAt==null?NaN:new Date(openedAt).getTime();
 const now=new Date(databaseNow).getTime();
 if(!Number.isFinite(start)||!Number.isFinite(now)||!Number.isInteger(durationSeconds)||durationSeconds<5||durationSeconds>600)return {valid:false,elapsedMs:0};
 const elapsedMs=Math.max(0,now-start);
 return {valid:now>=start&&elapsedMs<=durationSeconds*1000,elapsedMs};
}
