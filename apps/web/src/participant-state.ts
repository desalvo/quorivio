/** Pure participant-side rules shared by the UI and the CI acceptance contract. */
export type AnswerMode='single'|'multiple'|'text'|'file';
export function normalizeJoinCode(value:string):string{
 // Preserve URL-safe join secrets as well as short human-readable join codes.
 // Never let a pasted URL or encoded slash become an API route segment.
 let raw=value.trim();
 try{raw=decodeURIComponent(raw)}catch{return ''}
 if(raw.startsWith('/join/')||/^https?:\/\//i.test(raw)){
  try{const url=new URL(raw,'https://quorivio.invalid');const segments=url.pathname.split('/').filter(Boolean);raw=segments.length===2&&segments[0]==='join'?segments[1]:''}
  catch{return ''}
 }
 if(/^[a-f0-9]{10}$/i.test(raw))return raw.toUpperCase();
 return /^[a-zA-Z0-9_-]{1,128}$/.test(raw)?raw:raw.includes('/')||raw.includes('.')?'':raw.replace(/[^a-zA-Z0-9_-]/g,'').slice(0,128);
}
export function canSubmitParticipantAnswer(mode:string,required:boolean,value:{answer:string;multipleAnswers:string[];freeText:string}):boolean{
 if(!required)return true;
 if(mode==='multiple')return value.multipleAnswers.length>0;
 if(mode==='text')return value.freeText.trim().length>0;
 return value.answer.trim().length>0;
}
export function publicActivityFromSnapshot(snapshot:any):any|null{
 if(snapshot?.session?.status!=='active')return null;
 const id=snapshot.session.current_activity_id;
 if(!id||!Array.isArray(snapshot.activities))return null;
 return snapshot.activities.find((a:any)=>a?.id===id&&a.status==='open')||null;
}
export function nextLiveRetryMs(attempt:number):number{
 return Math.min(30000,1800*Math.pow(2,Math.max(0,Math.min(6,Math.floor(attempt)))));
}
