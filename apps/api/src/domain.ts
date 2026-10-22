export type SessionStatus = 'draft'|'ready'|'active'|'closed';
export type ActivityType = 'poll'|'quiz';
export type Activity = {id:string;session_id:string;type:ActivityType;title:string;options:{id:string;label:string}[];correct_option_id:string|null;duration_seconds:number|null;status:'pending'|'open'|'closed';position:number};
export function validTransition(from:SessionStatus,to:SessionStatus):boolean {return ({draft:['ready','active','closed'],ready:['active','closed'],active:['closed'],closed:[]}[from] as string[]).includes(to);}
export function checkAnswer(activity:Pick<Activity,'type'|'options'|'correct_option_id'>, optionId:string):boolean {return activity.type==='quiz' && activity.correct_option_id===optionId;}
export function validateOptions(options:unknown):options is {id:string;label:string}[] {return Array.isArray(options)&&options.length>=2&&options.length<=12&&options.every(o=>typeof o?.id==='string'&&/^[a-z0-9-]{1,40}$/i.test(o.id)&&typeof o?.label==='string'&&o.label.trim().length>0&&o.label.length<=160)&&new Set(options.map(o=>o.id)).size===options.length;}
export function publicActivity(activity:Activity){const {correct_option_id,...visible}=activity;return visible;}
