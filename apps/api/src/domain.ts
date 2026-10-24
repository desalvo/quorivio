export type SessionStatus = 'draft'|'ready'|'active'|'paused'|'closed';
export type ActivityType = 'poll'|'quiz'|'timed_quiz';
export type Activity = {id:string;session_id:string;type:ActivityType;title:string;options:{id:string;label:string}[];correct_option_id:string|null;duration_seconds:number|null;status:'pending'|'open'|'closed';position:number};
export function validTransition(from:SessionStatus,to:SessionStatus):boolean {return ({draft:['ready','active','closed'],ready:['active','closed'],active:['paused','closed'],paused:['active','closed'],closed:[]}[from] as string[]).includes(to);}
export function checkAnswer(activity:Pick<Activity,'type'|'options'|'correct_option_id'>, optionId:string):boolean {return (activity.type==='quiz'||activity.type==='timed_quiz') && activity.correct_option_id===optionId;}
export function validateOptions(options:unknown):options is {id:string;label:string}[] {return Array.isArray(options)&&options.length>=2&&options.length<=12&&options.every(o=>typeof o?.id==='string'&&/^[a-z0-9-]{1,40}$/i.test(o.id)&&typeof o?.label==='string'&&o.label.trim().length>0&&o.label.length<=160)&&new Set(options.map(o=>o.id)).size===options.length;}
export function publicActivity(activity:Activity){const {correct_option_id,...visible}=activity as Activity & {correct_option_ids?:string[]};delete (visible as any).correct_option_ids;;return visible;}

export function validRetentionDays(value:unknown):value is number{return Number.isInteger(value)&&typeof value==='number'&&value>=1&&value<=3650;}
/** Protect exported spreadsheet cells from formula injection, including prefixed whitespace. */
export function escapeCsvCell(value:unknown):string {const raw=String(value??'');const safe=/^[\s\u0000-\u001f]*[=+@-]/u.test(raw)?"'"+raw:raw;return '"'+safe.replace(/"/g,'""')+'"';}

export type WidgetTextStyle={fontFamily?:string;fontSize?:number;color?:string;bold?:boolean;italic?:boolean;underline?:boolean;strikethrough?:boolean;fillColor?:string;strokeColor?:string;rounded?:boolean;shapeType?:'ellipse'|'triangle';animation?:'none'|'fade'|'slide'};
export function validWidgetTextStyle(x:unknown):boolean {if(x===undefined)return true;if(!x||typeof x!=='object'||Array.isArray(x))return false;const v=x as Record<string,unknown>;if(Object.keys(v).some(k=>!['fontFamily','fontSize','color','bold','italic','underline','strikethrough','animation','fillColor','strokeColor','rounded','shapeType'].includes(k)))return false;return (v.fontFamily===undefined||['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].includes(String(v.fontFamily)))&&(v.fontSize===undefined||Number.isInteger(v.fontSize)&&Number(v.fontSize)>=10&&Number(v.fontSize)<=96)&&(v.color===undefined||typeof v.color==='string'&&/^#[0-9a-fA-F]{6}$/.test(v.color))&&['bold','italic','underline','strikethrough'].every(k=>v[k]===undefined||typeof v[k]==='boolean')&&['fillColor','strokeColor'].every(k=>v[k]===undefined||typeof v[k]==='string'&&/^#[0-9a-fA-F]{6}$/.test(v[k] as string))&&(v.rounded===undefined||typeof v.rounded==='boolean')&&(v.shapeType===undefined||['ellipse','triangle'].includes(String(v.shapeType)))&&(v.animation===undefined||['none','fade','slide'].includes(String(v.animation)))}
/** Percent-based canvas coordinates; reject NaN, negative widths and off-page elements. */
export function validWidgetPosition(value:unknown):boolean {
 if(!value||typeof value!=='object'||Array.isArray(value))return false;
 const v=value as Record<string,unknown>;
 if(Object.keys(v).some(k=>!['x','y','width','height','rotation'].includes(k)))return false;
 return ['x','y','width'].every(k=>typeof v[k]==='number'&&Number.isFinite(v[k]))&&Number(v.x)>=0&&Number(v.y)>=0&&Number(v.width)>=0.01&&Number(v.width)<=100&&Number(v.x)+Number(v.width)<=100&&Number(v.y)<=99&&(v.height===undefined||(typeof v.height==='number'&&Number.isFinite(v.height)&&Number(v.height)>=0.01&&Number(v.height)<=100&&Number(v.y)+Number(v.height)<=100))&&(v.rotation===undefined||(typeof v.rotation==='number'&&Number.isFinite(v.rotation)&&v.rotation>=-360&&v.rotation<=360));
}
export type PageDesign={backgroundAssetId?:string;backgroundUrl?:string;logos?:string[];header?:string;footer?:string;media?:{kind:'image'|'video'|'pdf';url:string;alt?:string}[];widgets?:{id:string;kind:'rating'|'reactions'|'text'|'divider'|'timer'|'qr'|'profile'|'question'|'postit'|'image'|'video'|'logo'|'pdf'|'topic-question'|'timed-quiz'|'results-button';label?:string;description?:string;answerMode?:'single'|'multiple'|'text'|'file';options?:{id:string;label:string}[];required?:boolean;style?:WidgetTextStyle;position?:{x:number;y:number;width:number;height?:number;rotation?:number};presenterId?:string;targetKind?:'question'|'quiz'|'session'|'presenter';targetId?:string;assetId?:string;showNames?:boolean}[]};
export function validPageDesign(x:unknown):x is PageDesign {
 if(x===null||typeof x!=='object'||Array.isArray(x))return false;
 const d=x as Record<string,unknown>;const keys=Object.keys(d);
 if(keys.some(k=>!['backgroundAssetId','backgroundUrl','logos','header','footer','media','widgets'].includes(k)))return false;
 const url=(v:unknown)=>typeof v==='string'&&v.length<=1024&&/^https:\/\/[^\s]+$/.test(v);
 if(d.backgroundAssetId!==undefined&&(typeof d.backgroundAssetId!=='string'||!uuidRegex.test(d.backgroundAssetId)))return false;
 if(d.backgroundUrl!==undefined&&!url(d.backgroundUrl))return false;
 if(d.logos!==undefined&&(!Array.isArray(d.logos)||d.logos.length>5||!d.logos.every(url)))return false;
 for(const key of ['header','footer'])if(d[key]!==undefined&&(typeof d[key]!=='string'||d[key].length>500))return false;
 if(d.media!==undefined&&(!Array.isArray(d.media)||d.media.length>8||!d.media.every((m:any)=>m&&['image','video','pdf'].includes(m.kind)&&url(m.url)&&(m.alt===undefined||(typeof m.alt==='string'&&m.alt.length<=240)))))return false;
 if(d.widgets!==undefined&&(!Array.isArray(d.widgets)||d.widgets.length>16||new Set(d.widgets.map((w:any)=>w?.id)).size!==d.widgets.length||!d.widgets.every((w:any)=>w&&typeof w.id==='string'&&/^[a-zA-Z0-9_-]{1,48}$/.test(w.id)&&['rating','reactions','text','divider','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count'].includes(w.kind)&&(w.kind!=='rating'||typeof w.label==='string'&&w.label.trim().length>0)&&(w.description===undefined||(typeof w.description==='string'&&w.description.length<=500))&&(w.answerMode===undefined||validAnswerMode(w.answerMode))&&(w.options===undefined||(Array.isArray(w.options)&&w.options.length<=12&&w.options.every((o:any)=>typeof o?.id==='string'&&/^[a-zA-Z0-9_-]{1,40}$/.test(o.id)&&typeof o?.label==='string'&&o.label.trim().length>0&&o.label.length<=160)&&new Set(w.options.map((o:any)=>o.id)).size===w.options.length))&&(w.required===undefined||typeof w.required==='boolean')&&(w.showNames===undefined||typeof w.showNames==='boolean')&&(w.durationSeconds===undefined||(Number.isInteger(w.durationSeconds)&&w.durationSeconds>=5&&w.durationSeconds<=600))&&(w.correctOptionId===undefined||typeof w.correctOptionId==='string')&&(w.correctOptionIds===undefined||(Array.isArray(w.correctOptionIds)&&w.correctOptionIds.every((id:any)=>typeof id==='string')))&&validWidgetTextStyle(w.style)&&(w.position===undefined||validWidgetPosition(w.position))&&(w.label===undefined||(typeof w.label==='string'&&w.label.length<=240))&&(w.presenterId===undefined||(typeof w.presenterId==='string'&&uuidRegex.test(w.presenterId)))&&(w.targetKind===undefined||['question','quiz','session','presenter'].includes(w.targetKind))&&(w.targetId===undefined||(typeof w.targetId==='string'&&uuidRegex.test(w.targetId)))&&(w.assetId===undefined||(typeof w.assetId==='string'&&uuidRegex.test(w.assetId)))&&(!['image','video','logo','pdf'].includes(w.kind)||(typeof w.assetId==='string'&&uuidRegex.test(w.assetId))))))return false;
 return true;
}
export function validPseudonym(value:unknown):value is string {return typeof value==='string'&&value.trim().length>=2&&value.trim().length<=40&&!/[<>\x00-\x1f]/.test(value)}


export type AnswerMode='single'|'multiple'|'text'|'file';
export const REACTION_EMOJIS=['👍','❤️','😂','😮','👏','🎉','🤔','😕'] as const;
export function validReaction(v:unknown):v is string {return typeof v==='string'&&REACTION_EMOJIS.includes(v as typeof REACTION_EMOJIS[number]);}
export function validAnswerMode(v:unknown):v is AnswerMode{return v==='single'||v==='multiple'||v==='text'||v==='file';}
export function validateSubmittedAnswer(mode:AnswerMode,required:boolean,value:unknown,options:{id:string;label:string}[]):{optionIds:string[];text:string|null;assetId:string|null}|null {
  if(value===null||value===undefined||value==='')return required?null:{optionIds:[],text:null,assetId:null};
  if(mode==='single'){if(typeof value!=='string'||!options.some(o=>o.id===value))return null;return {optionIds:[value],text:null,assetId:null};}
  if(mode==='multiple'){if(!Array.isArray(value)||value.length>12||!value.every(x=>typeof x==='string')||new Set(value).size!==value.length||!value.every(x=>options.some(o=>o.id===x))||required&&value.length===0)return null;return {optionIds:value,text:null,assetId:null};}
  if(mode==='text'){if(typeof value!=='string'||value.length>5000||required&&!value.trim())return null;return {optionIds:[],text:value,assetId:null};}
  if(mode==='file'){if(typeof value!=='string'||!uuidRegex.test(value))return null;return {optionIds:[],text:null,assetId:value};}
  return null;
}
const uuidRegex=/^[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
