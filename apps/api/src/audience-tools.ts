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
