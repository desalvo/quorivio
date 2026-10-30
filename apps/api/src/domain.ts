export type SessionStatus = 'draft'|'ready'|'active'|'paused'|'closed';
export type ActivityType = 'poll'|'quiz'|'timed_quiz';
export type Activity = {id:string;session_id:string;type:ActivityType;title:string;options:{id:string;label:string}[];correct_option_id:string|null;duration_seconds:number|null;status:'pending'|'open'|'closed';position:number};
export function validTransition(from:SessionStatus,to:SessionStatus):boolean {return ({draft:['ready','active','closed'],ready:['active','closed'],active:['paused','closed'],paused:['active','closed'],closed:[]}[from] as string[]).includes(to);}
export function checkAnswer(activity:Pick<Activity,'type'|'options'|'correct_option_id'>, optionId:string):boolean {return (activity.type==='quiz'||activity.type==='timed_quiz') && activity.correct_option_id===optionId;}
export function validateOptions(options:unknown):options is {id:string;label:string}[] {return Array.isArray(options)&&options.length>=2&&options.length<=12&&options.every(o=>typeof o?.id==='string'&&/^[a-z0-9-]{1,40}$/i.test(o.id)&&typeof o?.label==='string'&&o.label.trim().length>0&&o.label.length<=160)&&new Set(options.map(o=>o.id)).size===options.length;}
/** Audience-facing projection must never include answer keys, including nested quiz questions. */
export function publicActivity(activity:Activity){
 const {correct_option_id,...visible}=activity as Activity & {correct_option_ids?:string[];page_design?:PageDesign};
 delete visible.correct_option_ids;
 if(visible.page_design?.widgets){
  visible.page_design={...visible.page_design,widgets:visible.page_design.widgets.map(widget=>{
   if(widget.kind!=='timed-quiz'&&widget.kind!=='question')return widget;
   const {correctOptionId,correctOptionIds,...safe}=widget;
   return {...safe,questions:widget.questions?.map(question=>{
    const {correctOptionId,correctOptionIds,...publicQuestion}=question;
    return publicQuestion;
   })};
  })};
 }
 return visible;
}

export function validRetentionDays(value:unknown):value is number{return Number.isInteger(value)&&typeof value==='number'&&value>=1&&value<=3650;}
/** Protect exported spreadsheet cells from formula injection, including prefixed whitespace. */
export function escapeCsvCell(value:unknown):string {const raw=String(value??'');const safe=/^[\s\u0000-\u001f]*[=+@-]/u.test(raw)?"'"+raw:raw;return '"'+safe.replace(/"/g,'""')+'"';}

export type WidgetTextStyle={fontFamily?:string;fontSize?:number;color?:string;bold?:boolean;italic?:boolean;underline?:boolean;strikethrough?:boolean;textAlign?:'left'|'center'|'right';verticalAlign?:'top'|'middle'|'bottom';fillColor?:string;fillNone?:boolean;strokeColor?:string;strokeNone?:boolean;strokeWidth?:number;strokeDash?:'solid'|'dash'|'dot';rounded?:boolean;shapeType?:'rectangle'|'rounded-rectangle'|'ellipse'|'circle'|'triangle'|'diamond'|'cloud'|'speech'|'hexagon';fillOpacity?:number;fillMode?:'solid'|'gradient'|'image';gradientEndColor?:string;fillImageAssetId?:string;ratingView?:'buttons'|'select';animation?:'none'|'fade'|'slide';artTheme?:'studio'|'glass'|'playful'|'minimal';artEffect?:'none'|'float'|'glow'|'tilt';timerFace?:'hourglass'|'dial'|'digital'};
export function validWidgetTextStyle(x:unknown):boolean {if(x===undefined)return true;if(!x||typeof x!=='object'||Array.isArray(x))return false;const v=x as Record<string,unknown>;if(Object.keys(v).some(k=>!['fontFamily','fontSize','color','bold','italic','underline','strikethrough','textAlign','verticalAlign','animation','fillColor','fillNone','strokeColor','strokeNone','strokeWidth','strokeDash','rounded','shapeType','fillOpacity','fillMode','gradientEndColor','fillImageAssetId','ratingView','artTheme','artEffect','timerFace'].includes(k)))return false;return (v.fontFamily===undefined||['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].includes(String(v.fontFamily)))&&(v.fontSize===undefined||Number.isInteger(v.fontSize)&&Number(v.fontSize)>=10&&Number(v.fontSize)<=96)&&(v.color===undefined||typeof v.color==='string'&&/^#[0-9a-fA-F]{6}$/.test(v.color))&&['bold','italic','underline','strikethrough'].every(k=>v[k]===undefined||typeof v[k]==='boolean')&&['fillColor','strokeColor','gradientEndColor'].every(k=>v[k]===undefined||typeof v[k]==='string'&&/^#[0-9a-fA-F]{6}$/.test(v[k] as string))&&['fillNone','strokeNone'].every(k=>v[k]===undefined||typeof v[k]==='boolean')&&(v.strokeWidth===undefined||(typeof v.strokeWidth==='number'&&Number.isFinite(v.strokeWidth)&&v.strokeWidth>=0.25&&v.strokeWidth<=12))&&(v.strokeDash===undefined||['solid','dash','dot'].includes(String(v.strokeDash)))&&(v.textAlign===undefined||['left','center','right'].includes(String(v.textAlign)))&&(v.verticalAlign===undefined||['top','middle','bottom'].includes(String(v.verticalAlign)))&&(v.rounded===undefined||typeof v.rounded==='boolean')&&(v.shapeType===undefined||['rectangle','rounded-rectangle','ellipse','circle','triangle','diamond','cloud','speech','hexagon'].includes(String(v.shapeType)))&&(v.fillMode===undefined||['solid','gradient','image'].includes(String(v.fillMode)))&&(v.ratingView===undefined||['buttons','select'].includes(String(v.ratingView)))&&(v.fillOpacity===undefined||(typeof v.fillOpacity==='number'&&Number.isFinite(v.fillOpacity)&&v.fillOpacity>=0&&v.fillOpacity<=1))&&(v.fillImageAssetId===undefined||(typeof v.fillImageAssetId==='string'&&uuidRegex.test(v.fillImageAssetId)))&&(v.animation===undefined||['none','fade','slide'].includes(String(v.animation)))&&(v.artTheme===undefined||['studio','glass','playful','minimal'].includes(String(v.artTheme)))&&(v.artEffect===undefined||['none','float','glow','tilt'].includes(String(v.artEffect)))&&(v.timerFace===undefined||['hourglass','dial','digital'].includes(String(v.timerFace)))}
/** Percent-based canvas coordinates; reject NaN, negative widths and off-page elements. */
export function validWidgetPosition(value:unknown):boolean {
 if(!value||typeof value!=='object'||Array.isArray(value))return false;
 const v=value as Record<string,unknown>;
 if(Object.keys(v).some(k=>!['x','y','width','height','rotation'].includes(k)))return false;
 return ['x','y','width'].every(k=>typeof v[k]==='number'&&Number.isFinite(v[k]))&&Number(v.x)>=0&&Number(v.y)>=0&&Number(v.width)>=0.01&&Number(v.width)<=100&&Number(v.x)+Number(v.width)<=100&&Number(v.y)<=99&&(v.height===undefined||(typeof v.height==='number'&&Number.isFinite(v.height)&&Number(v.height)>=0.01&&Number(v.height)<=100&&Number(v.y)+Number(v.height)<=100))&&(v.rotation===undefined||(typeof v.rotation==='number'&&Number.isFinite(v.rotation)&&v.rotation>=-360&&v.rotation<=360));
}
export type PictureCrop={left:number;right:number;top:number;bottom:number};
export function validPictureCrop(x:unknown):x is PictureCrop {if(!x||typeof x!=='object'||Array.isArray(x))return false;const c=x as Record<string,unknown>;if(Object.keys(c).length!==4||Object.keys(c).some(k=>!['left','right','top','bottom'].includes(k)))return false;return ['left','right','top','bottom'].every(k=>typeof c[k]==='number'&&Number.isFinite(c[k])&&Number(c[k])>=0&&Number(c[k])<=0.95)&&Number(c.left)+Number(c.right)<0.99&&Number(c.top)+Number(c.bottom)<0.99;}
export type WidgetInlineMark={field:string;start:number;end:number;style:Partial<Pick<WidgetTextStyle,'fontFamily'|'fontSize'|'color'|'bold'|'italic'|'underline'|'strikethrough'>>};
/** Plain text plus bounded styles, never serialized HTML or arbitrary CSS. */
export function validWidgetInlineMarks(x:unknown):boolean{
 if(x===undefined)return true;
 if(!Array.isArray(x)||x.length>64)return false;
 return x.every(mark=>{
  if(!mark||typeof mark!=='object'||Array.isArray(mark))return false;
  const m=mark as Record<string,unknown>;
  if(Object.keys(m).some(k=>!['field','start','end','style'].includes(k)))return false;
  if(typeof m.field!=='string'||!(/^(label|description|option:[A-Za-z0-9_-]{1,40}|question:[A-Za-z0-9_-]{1,40}:(label|description)|question:[A-Za-z0-9_-]{1,40}:option:[A-Za-z0-9_-]{1,40})$/.test(m.field)))return false;
  if(!Number.isInteger(m.start)||!Number.isInteger(m.end)||!(Number(m.start)>=0&&Number(m.end)>Number(m.start)&&Number(m.end)<=500))return false;
  if(!m.style||typeof m.style!=='object'||Array.isArray(m.style))return false;
  const v=m.style as Record<string,unknown>;
  if(Object.keys(v).some(k=>!['fontFamily','fontSize','color','bold','italic','underline','strikethrough'].includes(k)))return false;
  return validWidgetTextStyle(v);
 });
}
/** A question-group keeps independent answer identities inside one visual widget. The
 * legacy top-level question is used only when questions is absent. */
export type WidgetSubquestion={id:string;label:string;description?:string;answerMode?:'single'|'multiple'|'text'|'file';options?:{id:string;label:string}[];required?:boolean;allowAnswerChange?:boolean;correctOptionId?:string;correctOptionIds?:string[]};
export function validWidgetSubquestions(value:unknown,kind:string):boolean{
 if(value===undefined)return true;
 if(!['question','timed-quiz'].includes(kind)||!Array.isArray(value)||value.length<1||value.length>5)return false;
 const ids=new Set<string>();
 return value.every((q:unknown)=>{
  if(!q||typeof q!=='object'||Array.isArray(q))return false;
  const v=q as Record<string,unknown>;
  if(Object.keys(v).some(k=>!['id','label','description','answerMode','options','required','allowAnswerChange','correctOptionId','correctOptionIds'].includes(k)))return false;
  if(typeof v.id!=='string'||!/^[a-zA-Z0-9_-]{1,40}$/.test(v.id)||ids.has(v.id))return false;ids.add(v.id);
  if(typeof v.label!=='string'||!v.label.trim()||v.label.length>240||v.description!==undefined&&(typeof v.description!=='string'||v.description.length>500))return false;
  if(v.allowAnswerChange!==undefined&&typeof v.allowAnswerChange!=='boolean')return false;
  const mode=v.answerMode||'text';if(!validAnswerMode(mode)||kind==='timed-quiz'&&!['single','multiple'].includes(mode))return false;
  if(v.required!==undefined&&typeof v.required!=='boolean')return false;
  if(v.options!==undefined&&(!Array.isArray(v.options)||v.options.length>12||!v.options.every((o:any)=>typeof o?.id==='string'&&/^[a-zA-Z0-9_-]{1,40}$/.test(o.id)&&typeof o?.label==='string'&&!!o.label.trim()&&o.label.length<=160)||new Set(v.options.map((o:any)=>o.id)).size!==v.options.length))return false;
  if(['single','multiple'].includes(String(mode))&&(!Array.isArray(v.options)||v.options.length<2))return false;
  if(v.correctOptionId!==undefined&&(typeof v.correctOptionId!=='string'||!(Array.isArray(v.options)&&v.options.some((o:any)=>o.id===v.correctOptionId))))return false;
  if(v.correctOptionIds!==undefined&&(!Array.isArray(v.correctOptionIds)||new Set(v.correctOptionIds).size!==v.correctOptionIds.length||!v.correctOptionIds.every((id:any)=>typeof id==='string'&&(Array.isArray(v.options)&&v.options.some((o:any)=>o.id===id)))))return false;
  return true;
 });
}
export function questionParts(widget:{questions?:WidgetSubquestion[]}):WidgetSubquestion[]{return widget.questions?.length?widget.questions:[]}
export type PageDesign={backgroundColor?:string;backgroundAssetId?:string;backgroundUrl?:string;logos?:string[];header?:string;footer?:string;media?:{kind:'image'|'video'|'pdf';url:string;alt?:string}[];widgets?:{id:string;kind:'rating'|'reactions'|'text'|'divider'|'timer'|'qr'|'profile'|'question'|'postit'|'image'|'video'|'logo'|'pdf'|'topic-question'|'timed-quiz'|'results-button'|'participant-count';label?:string;description?:string;answerMode?:'single'|'multiple'|'text'|'file';options?:{id:string;label:string}[];questions?:WidgetSubquestion[];required?:boolean;durationSeconds?:number;correctOptionId?:string;correctOptionIds?:string[];resultsView?:'bars'|'pie'|'table'|'cloud';style?:WidgetTextStyle;textMarks?:WidgetInlineMark[];position?:{x:number;y:number;width:number;height?:number;rotation?:number};presenterId?:string;showEmail?:boolean;allowAnswerChange?:boolean;targetKind?:'question'|'quiz'|'session'|'presenter';targetId?:string;targetWidgetId?:string;targetQuestionId?:string;assetId?:string;crop?:PictureCrop;showNames?:boolean}[]};
export function validPageDesign(x:unknown):x is PageDesign {
 if(x===null||typeof x!=='object'||Array.isArray(x))return false;
 const d=x as Record<string,unknown>;const keys=Object.keys(d);
 if(keys.some(k=>!['backgroundColor','backgroundAssetId','backgroundUrl','logos','header','footer','media','widgets'].includes(k)))return false;
 const url=(v:unknown)=>typeof v==='string'&&v.length<=1024&&/^https:\/\/[^\s]+$/.test(v);
 if(d.backgroundColor!==undefined&&(typeof d.backgroundColor!=='string'||!/^#[0-9a-fA-F]{6}$/.test(d.backgroundColor)))return false;
 if(d.backgroundAssetId!==undefined&&(typeof d.backgroundAssetId!=='string'||!uuidRegex.test(d.backgroundAssetId)))return false;
 if(d.backgroundUrl!==undefined&&!url(d.backgroundUrl))return false;
 if(d.logos!==undefined&&(!Array.isArray(d.logos)||d.logos.length>5||!d.logos.every(url)))return false;
 for(const key of ['header','footer'])if(d[key]!==undefined&&(typeof d[key]!=='string'||d[key].length>500))return false;
 if(d.media!==undefined&&(!Array.isArray(d.media)||d.media.length>8||!d.media.every((m:any)=>m&&['image','video','pdf'].includes(m.kind)&&url(m.url)&&(m.alt===undefined||(typeof m.alt==='string'&&m.alt.length<=240)))))return false;
 if(d.widgets!==undefined&&(!Array.isArray(d.widgets)||d.widgets.length>16||new Set(d.widgets.map((w:any)=>w?.id)).size!==d.widgets.length||!d.widgets.every((w:any)=>w&&typeof w.id==='string'&&/^[a-zA-Z0-9_-]{1,48}$/.test(w.id)&&['rating','reactions','text','divider','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count'].includes(w.kind)&&(w.kind!=='rating'||typeof w.label==='string'&&w.label.trim().length>0)&&(w.description===undefined||(typeof w.description==='string'&&w.description.length<=500))&&(w.answerMode===undefined||validAnswerMode(w.answerMode))&&(w.options===undefined||(Array.isArray(w.options)&&w.options.length<=12&&w.options.every((o:any)=>typeof o?.id==='string'&&/^[a-zA-Z0-9_-]{1,40}$/.test(o.id)&&typeof o?.label==='string'&&o.label.trim().length>0&&o.label.length<=160)&&new Set(w.options.map((o:any)=>o.id)).size===w.options.length))&&validWidgetSubquestions(w.questions,w.kind)&&(w.required===undefined||typeof w.required==='boolean')&&(w.resultsView===undefined||['bars','pie','table','cloud'].includes(w.resultsView))&&(w.showNames===undefined||typeof w.showNames==='boolean')&&(w.showEmail===undefined||(w.kind==='profile'&&typeof w.showEmail==='boolean'))&&(w.allowAnswerChange===undefined||(['question','timed-quiz'].includes(w.kind)&&typeof w.allowAnswerChange==='boolean'))&&(w.durationSeconds===undefined||(Number.isInteger(w.durationSeconds)&&w.durationSeconds>=5&&w.durationSeconds<=600))&&(w.correctOptionId===undefined||typeof w.correctOptionId==='string')&&(w.correctOptionIds===undefined||(Array.isArray(w.correctOptionIds)&&w.correctOptionIds.every((id:any)=>typeof id==='string')))&&validWidgetTextStyle(w.style)&&validWidgetInlineMarks(w.textMarks)&&(w.textMarks===undefined||w.textMarks.every((mark:any)=>{const field=mark.field as string;const value=field==='label'?w.label:field==='description'?w.description:w.options?.find((option:any)=>'option:'+option.id===field)?.label ?? (field.startsWith('question:') ? (()=>{const parts=field.split(':');const q=w.questions?.find((item:any)=>item.id===parts[1]);return parts[2]==='label'?q?.label:parts[2]==='description'?q?.description:parts[2]==='option'?q?.options?.find((o:any)=>o.id===parts[3])?.label:undefined})() : undefined);return typeof value==='string'&&mark.end<=value.length}))&&(w.position===undefined||validWidgetPosition(w.position))&&(w.label===undefined||(typeof w.label==='string'&&w.label.length<=240))&&(w.presenterId===undefined||(typeof w.presenterId==='string'&&uuidRegex.test(w.presenterId)))&&(w.targetKind===undefined||['question','quiz','session','presenter'].includes(w.targetKind))&&(w.targetId===undefined||(typeof w.targetId==='string'&&uuidRegex.test(w.targetId)))&&(w.targetWidgetId===undefined||(w.kind==='results-button'&&typeof w.targetWidgetId==='string'&&/^[a-zA-Z0-9_-]{1,48}$/.test(w.targetWidgetId)))&&(w.targetQuestionId===undefined||(w.kind==='results-button'&&typeof w.targetQuestionId==='string'&&/^[a-zA-Z0-9_-]{1,40}$/.test(w.targetQuestionId)))&&(w.assetId===undefined||(typeof w.assetId==='string'&&uuidRegex.test(w.assetId)))&&(w.crop===undefined||(['image','logo'].includes(w.kind)&&validPictureCrop(w.crop)))&&(!['image','video','logo','pdf'].includes(w.kind)||(typeof w.assetId==='string'&&uuidRegex.test(w.assetId))))))return false;
 // Result widgets may only reference an eligible, distinct source on this very page.
 // Legacy unlinked result widgets remain loadable so the editor can repair them.
 if(Array.isArray(d.widgets))for(const widget of d.widgets){
  if(widget.kind!=='results-button'||widget.targetWidgetId===undefined)continue;
  const target=d.widgets.find((source:any)=>source.id===widget.targetWidgetId);
  if(!target||!['question','timed-quiz','rating','reactions','topic-question'].includes(target.kind))return false;
  if(widget.targetQuestionId!==undefined&&(!['question','timed-quiz'].includes(target.kind)||!target.questions?.some((q:any)=>q.id===widget.targetQuestionId)))return false;
 }
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
