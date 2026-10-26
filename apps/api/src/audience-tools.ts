/** Shared validation for audience-generated content; outputs are always rendered as text. */
export function normalizeWord(value: unknown): string | null {
 if (typeof value !== 'string') return null;
 const word=value.normalize('NFKC').trim().replace(/\s+/g,' ');
 if (word.length<1 || word.length>48 || /[<>\x00-\x1f\x7f]/u.test(word)) return null;
 return word.toLocaleLowerCase('en');
}
export function validateQuestion(value: unknown): string | null {
 if (typeof value!=='string') return null;
 const v=value.trim();
 if (v.length<5 || v.length>500 || /[\x00-\x08\x0b\x0c\x0e-\x1f]/u.test(v))return null;
 return v;
}
export type ModerationStatus='pending'|'approved'|'rejected';
export function moderationStatus(v:unknown):v is ModerationStatus{return v==='pending'||v==='approved'||v==='rejected'}
export function safeFrequency(entries:{word:string;count:number}[]):{word:string;count:number}[]{return entries.filter(x=>typeof x.word==='string'&&x.word.length>0&&x.word.length<=48&&Number.isSafeInteger(x.count)&&x.count>=0).sort((a,b)=>b.count-a.count||a.word.localeCompare(b.word)).slice(0,100)}

/** Strict bounded pagination shared by the presenter moderation API. */
export function parseModerationQueueQuery(status:unknown,page:unknown):{status:ModerationStatus|'all';page:number;offset:number}|null{
 const state=status===undefined?'pending':status;
 if(state!=='all'&&!moderationStatus(state))return null;
 const number=page===undefined?1:Number(page);
 if(typeof page!=='undefined'&&(typeof page!=='string'||!/^\d{1,5}$/.test(page)))return null;
 if(!Number.isSafeInteger(number)||number<1||number>10000)return null;
 return {status:state,page:number,offset:(number-1)*20};
}

/** Fail closed on mixed-session or oversized bulk moderation. */
export function parseModerationBulk(value:unknown):{status:'approved'|'rejected';ids:string[]}|null{
 if(!value||typeof value!=='object'||Array.isArray(value))return null;
 const v=value as Record<string,unknown>;
 if(v.status!=='approved'&&v.status!=='rejected')return null;
 if(!Array.isArray(v.ids)||v.ids.length<1||v.ids.length>20)return null;
 const ids=v.ids;
 if(!ids.every((id:unknown)=>typeof id==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)))return null;
 if(new Set(ids).size!==ids.length)return null;
 return {status:v.status,ids};
}
