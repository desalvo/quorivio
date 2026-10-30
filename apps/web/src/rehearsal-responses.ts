/** Rehearsal-only answer state: a draft changes presenter totals ONLY on submit.
 * These functions have no HTTP or persistent storage dependencies. */
export type DemoAnswer=string|string[];
export const REHEARSAL_REACTION_PREFIX='reaction-page:';
export function canSubmitRehearsalAnswer(mode:string,answer:DemoAnswer|undefined):boolean{
 if(mode==='single'||mode==='rating'||mode==='reaction')return typeof answer==='string'&&answer.length>0;
 if(mode==='multiple')return Array.isArray(answer)&&answer.length>0;
 if(mode==='text')return typeof answer==='string'&&answer.trim().length>0&&answer.length<=5000;
 // A file preview records only the filename; the bytes never leave this browser.
 if(mode==='file')return typeof answer==='string'&&answer.length>0&&answer.length<=255;
 return false;
}
/** One logical answer per widget/question in one rehearsal opening. Repeated clicks
 * cannot modify an already submitted answer. A fresh rehearsal resets state. */
export function commitRehearsalAnswer<T extends Record<string,DemoAnswer>>(
 submitted:T,key:string,value:DemoAnswer|undefined,mode:string
):T{
 if(!key||Object.hasOwn(submitted,key)||!canSubmitRehearsalAnswer(mode,value))return submitted;
 return {...submitted,[key]:Array.isArray(value)?[...value]:value} as T;
}

/** A reaction is a replaceable per-participant choice (one vote in totals), unlike a quiz answer. */
export function changeRehearsalReaction<T extends Record<string,DemoAnswer>>(state:T,pageKey:string,widgetId:string,emoji:string):T{
 if(!pageKey||!widgetId||!emoji)return state;
 if(state[pageKey]===emoji&&state[widgetId]===emoji)return state;
 return {...state,[pageKey]:emoji,[widgetId]:emoji};
}
