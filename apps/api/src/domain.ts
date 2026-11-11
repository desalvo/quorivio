export type SessionStatus = 'draft'|'ready'|'active'|'paused'|'closed';
export type ActivityType = 'poll'|'quiz'|'timed_quiz';
export type Activity = {id:string;session_id:string;type:ActivityType;title:string;options:{id:string;label:string}[];correct_option_id:string|null;duration_seconds:number|null;status:'pending'|'open'|'closed';position:number};
export function validTransition(from:SessionStatus,to:SessionStatus):boolean {return ({draft:['ready','active','closed'],ready:['active','closed'],active:['paused','closed'],paused:['active','closed'],closed:[]}[from] as string[]).includes(to);}
export function checkAnswer(activity:Pick<Activity,'type'|'options'|'correct_option_id'>, optionId:string):boolean {return (activity.type==='quiz'||activity.type==='timed_quiz') && activity.correct_option_id===optionId;}
export function validateOptions(options:unknown):options is {id:string;label:string}[] {return Array.isArray(options)&&options.length>=2&&options.length<=12&&options.every(o=>typeof o?.id==='string'&&/^[a-z0-9-]{1,40}$/i.test(o.id)&&typeof o?.label==='string'&&o.label.trim().length>0&&o.label.length<=255)&&new Set(options.map(o=>o.id)).size===options.length;}
/** Never publish answer keys in any audience-visible page, results design or
 * master template. The only authorized disclosure is a private POST response
 * after the participant has actually submitted an answer. */
export function publicPageDesign(design?:PageDesign):PageDesign|undefined {
 if(!design?.widgets)return design;
 return {...design,widgets:design.widgets.map(widget=>{
  const {correctOptionId,correctOptionIds,...safe}=widget;
  return {...safe,questions:widget.questions?.map(question=>{
   const {correctOptionId,correctOptionIds,...publicQuestion}=question;
   return publicQuestion;
  })};
 })};
}
export function publicTheme(theme:unknown):unknown {
 if(!theme||typeof theme!=='object'||Array.isArray(theme))return theme;
 const value=theme as Record<string,any>;
 if(!value.master?.widgets)return theme;
 return {...value,master:{...value.master,widgets:publicPageDesign({widgets:value.master.widgets})?.widgets}};
}
export function publicActivity(activity:Activity){
 const {correct_option_id,...visible}=activity as Activity & {correct_option_ids?:string[];page_design?:PageDesign;result_design?:PageDesign};
 delete visible.correct_option_ids;
 if(visible.page_design)visible.page_design=publicPageDesign(visible.page_design);
 if(visible.result_design)visible.result_design=publicPageDesign(visible.result_design);
 return visible;
}

export function validRetentionDays(value:unknown):value is number{return Number.isInteger(value)&&typeof value==='number'&&value>=1&&value<=3650;}
/** Protect exported spreadsheet cells from formula injection, including prefixed whitespace. */
export function escapeCsvCell(value:unknown):string {const raw=String(value??'');const safe=/^[\s\u0000-\u001f]*[=+@-]/u.test(raw)?"'"+raw:raw;return '"'+safe.replace(/"/g,'""')+'"';}

export type WidgetTextStyle={fontFamily?:string;fontSize?:number;color?:string;bold?:boolean;italic?:boolean;underline?:boolean;strikethrough?:boolean;textAlign?:'left'|'center'|'right';verticalAlign?:'top'|'middle'|'bottom';fillColor?:string;answerFillColor?:string;answerFontFamily?:string;answerFontSize?:number;answerFieldWidth?:number;answerFieldHeight?:number;answerColor?:string;answerBold?:boolean;answerItalic?:boolean;answerUnderline?:boolean;answerStrikethrough?:boolean;submitButtonSize?:number;submitFontFamily?:string;submitColor?:string;submitBold?:boolean;submitItalic?:boolean;submitUnderline?:boolean;submitStrikethrough?:boolean;footerNumberBold?:boolean;footerNumberItalic?:boolean;footerNumberUnderline?:boolean;footerNumberStrikethrough?:boolean;fillNone?:boolean;strokeColor?:string;strokeNone?:boolean;strokeWidth?:number;strokeDash?:'solid'|'dash'|'dot';rounded?:boolean;shapeType?:'rectangle'|'rounded-rectangle'|'ellipse'|'circle'|'triangle'|'diamond'|'cloud'|'speech'|'hexagon'|'pentagon'|'star'|'arrow'|'heart';fillOpacity?:number;fillMode?:'solid'|'gradient'|'image';gradientEndColor?:string;fillImageAssetId?:string;ratingView?:'buttons'|'select';ratingButtonSize?:number;footerNumberFontFamily?:string;footerNumberFontSize?:number;footerNumberColor?:string;footerNumberPaddingRight?:number;footerNumberPaddingBottom?:number;animation?:'none'|'fade'|'slide';artTheme?:'studio'|'glass'|'playful'|'minimal';artEffect?:'none'|'float'|'glow'|'tilt';sourceQuestionColor?:string;timerFace?:'hourglass'|'dial'|'digital';lineDirection?:'horizontal'|'vertical'|'diagonal'|'reverse';lineArrow?:'none'|'start'|'end'|'both'};
export function validWidgetTextStyle(x:unknown):boolean {if(x===undefined)return true;if(!x||typeof x!=='object'||Array.isArray(x))return false;const v=x as Record<string,unknown>;if(Object.keys(v).some(k=>!['fontFamily','fontSize','color','bold','italic','underline','strikethrough','textAlign','verticalAlign','animation','fillColor','answerFillColor','answerFontFamily','answerFontSize','answerFieldWidth','answerFieldHeight','answerColor','answerBold','answerItalic','answerUnderline','answerStrikethrough','submitButtonSize','submitFontFamily','submitColor','submitBold','submitItalic','submitUnderline','submitStrikethrough','footerNumberBold','footerNumberItalic','footerNumberUnderline','footerNumberStrikethrough','fillNone','strokeColor','strokeNone','strokeWidth','strokeDash','rounded','shapeType','fillOpacity','fillMode','gradientEndColor','fillImageAssetId','ratingView','ratingButtonSize','footerNumberFontFamily','footerNumberFontSize','footerNumberColor','sourceQuestionColor','footerNumberPaddingRight','footerNumberPaddingBottom','artTheme','artEffect','timerFace','lineDirection','lineArrow'].includes(k)))return false;return (v.fontFamily===undefined||['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].includes(String(v.fontFamily)))&&(v.fontSize===undefined||Number.isInteger(v.fontSize)&&Number(v.fontSize)>=10&&Number(v.fontSize)<=96)&&(v.color===undefined||typeof v.color==='string'&&/^#[0-9a-fA-F]{6}$/.test(v.color))&&['bold','italic','underline','strikethrough','answerBold','answerItalic','answerUnderline','answerStrikethrough','submitBold','submitItalic','submitUnderline','submitStrikethrough','footerNumberBold','footerNumberItalic','footerNumberUnderline','footerNumberStrikethrough'].every(k=>v[k]===undefined||typeof v[k]==='boolean')&&(v.submitFontFamily===undefined||['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].includes(String(v.submitFontFamily)))&&(v.answerFontFamily===undefined||['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].includes(String(v.answerFontFamily)))&&(v.answerFontSize===undefined||Number.isInteger(v.answerFontSize)&&Number(v.answerFontSize)>=10&&Number(v.answerFontSize)<=96)&&(v.answerFieldWidth===undefined||Number.isInteger(v.answerFieldWidth)&&Number(v.answerFieldWidth)>=25&&Number(v.answerFieldWidth)<=100)&&(v.answerFieldHeight===undefined||Number.isInteger(v.answerFieldHeight)&&Number(v.answerFieldHeight)>=48&&Number(v.answerFieldHeight)<=400)&&(v.submitButtonSize===undefined||Number.isInteger(v.submitButtonSize)&&Number(v.submitButtonSize)>=12&&Number(v.submitButtonSize)<=40)&&(v.submitColor===undefined||typeof v.submitColor==='string'&&/^#[0-9a-fA-F]{6}$/.test(v.submitColor))&&(v.answerColor===undefined||typeof v.answerColor==='string'&&/^#[0-9a-fA-F]{6}$/.test(v.answerColor))&&(v.sourceQuestionColor===undefined||typeof v.sourceQuestionColor==='string'&&/^#[0-9a-fA-F]{6}$/.test(v.sourceQuestionColor))&&['fillColor','answerFillColor','strokeColor','gradientEndColor'].every(k=>v[k]===undefined||typeof v[k]==='string'&&/^#[0-9a-fA-F]{6}$/.test(v[k] as string))&&['fillNone','strokeNone'].every(k=>v[k]===undefined||typeof v[k]==='boolean')&&(v.strokeWidth===undefined||(typeof v.strokeWidth==='number'&&Number.isFinite(v.strokeWidth)&&v.strokeWidth>=0&&v.strokeWidth<=12))&&(v.strokeDash===undefined||['solid','dash','dot'].includes(String(v.strokeDash)))&&(v.textAlign===undefined||['left','center','right'].includes(String(v.textAlign)))&&(v.verticalAlign===undefined||['top','middle','bottom'].includes(String(v.verticalAlign)))&&(v.rounded===undefined||typeof v.rounded==='boolean')&&(v.shapeType===undefined||['rectangle','rounded-rectangle','ellipse','circle','triangle','diamond','cloud','speech','hexagon','pentagon','star','arrow','heart'].includes(String(v.shapeType)))&&(v.fillMode===undefined||['solid','gradient','image'].includes(String(v.fillMode)))&&(v.ratingView===undefined||['buttons','select'].includes(String(v.ratingView)))&&(v.ratingButtonSize===undefined||Number.isInteger(v.ratingButtonSize)&&Number(v.ratingButtonSize)>=10&&Number(v.ratingButtonSize)<=64)&&(v.footerNumberFontFamily===undefined||['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].includes(String(v.footerNumberFontFamily)))&&(v.footerNumberFontSize===undefined||Number.isInteger(v.footerNumberFontSize)&&Number(v.footerNumberFontSize)>=8&&Number(v.footerNumberFontSize)<=96)&&(v.footerNumberColor===undefined||typeof v.footerNumberColor==='string'&&/^#[0-9a-fA-F]{6}$/.test(v.footerNumberColor))&&['footerNumberPaddingRight','footerNumberPaddingBottom'].every(k=>v[k]===undefined||Number.isInteger(v[k])&&Number(v[k])>=0&&Number(v[k])<=80)&&(v.fillOpacity===undefined||(typeof v.fillOpacity==='number'&&Number.isFinite(v.fillOpacity)&&v.fillOpacity>=0&&v.fillOpacity<=1))&&(v.fillImageAssetId===undefined||(typeof v.fillImageAssetId==='string'&&uuidRegex.test(v.fillImageAssetId)))&&(v.animation===undefined||['none','fade','slide'].includes(String(v.animation)))&&(v.artTheme===undefined||['studio','glass','playful','minimal'].includes(String(v.artTheme)))&&(v.artEffect===undefined||['none','float','glow','tilt'].includes(String(v.artEffect)))&&(v.timerFace===undefined||['hourglass','dial','digital'].includes(String(v.timerFace)))&&(v.lineDirection===undefined||['horizontal','vertical','diagonal','reverse'].includes(String(v.lineDirection)))&&(v.lineArrow===undefined||['none','start','end','both'].includes(String(v.lineArrow)))}
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
export type WidgetSubquestion={id:string;label:string;description?:string;answerMode?:'single'|'multiple'|'text'|'file';options?:{id:string;label:string}[];required?:boolean;allowAnswerChange?:boolean;correctOptionId?:string;correctOptionIds?:string[];answerKeyEnabled?:boolean};
export function validWidgetSubquestions(value:unknown,kind:string):boolean{
 if(value===undefined)return true;
 if(!['question','timed-quiz'].includes(kind)||!Array.isArray(value)||value.length<1||value.length>5)return false;
 const ids=new Set<string>();
 return value.every((q:unknown)=>{
  if(!q||typeof q!=='object'||Array.isArray(q))return false;
  const v=q as Record<string,unknown>;
  if(Object.keys(v).some(k=>!['id','label','description','answerMode','options','required','allowAnswerChange','correctOptionId','correctOptionIds','answerKeyEnabled'].includes(k)))return false;
  if(typeof v.id!=='string'||!/^[a-zA-Z0-9_-]{1,40}$/.test(v.id)||ids.has(v.id))return false;ids.add(v.id);
  if(typeof v.label!=='string'||!v.label.trim()||v.label.length>240||v.description!==undefined&&(typeof v.description!=='string'||v.description.length>500))return false;
  if(v.allowAnswerChange!==undefined&&typeof v.allowAnswerChange!=='boolean')return false;
  const mode=v.answerMode||'text';if(!validAnswerMode(mode)||kind==='timed-quiz'&&!['single','multiple'].includes(mode))return false;
  if(v.required!==undefined&&typeof v.required!=='boolean')return false;
  if(v.options!==undefined&&(!Array.isArray(v.options)||v.options.length>12||!v.options.every((o:any)=>typeof o?.id==='string'&&/^[a-zA-Z0-9_-]{1,40}$/.test(o.id)&&typeof o?.label==='string'&&!!o.label.trim()&&o.label.length<=255)||new Set(v.options.map((o:any)=>o.id)).size!==v.options.length))return false;
  if(['single','multiple'].includes(String(mode))&&(!Array.isArray(v.options)||v.options.length<2))return false;
  if(v.answerKeyEnabled!==undefined&&typeof v.answerKeyEnabled!=='boolean')return false;
  if(v.answerKeyEnabled===true&&(!['single','multiple'].includes(mode)||kind!=='question'&&kind!=='timed-quiz'))return false;
  if(v.answerKeyEnabled===true&&mode==='single'&&Array.isArray(v.correctOptionIds)&&v.correctOptionIds.length>1)return false;
  if(v.correctOptionId!==undefined&&(typeof v.correctOptionId!=='string'||!(Array.isArray(v.options)&&v.options.some((o:any)=>o.id===v.correctOptionId))))return false;
  if(v.correctOptionIds!==undefined&&(!Array.isArray(v.correctOptionIds)||new Set(v.correctOptionIds).size!==v.correctOptionIds.length||!v.correctOptionIds.every((id:any)=>typeof id==='string'&&(Array.isArray(v.options)&&v.options.some((o:any)=>o.id===id)))))return false;
  return true;
 });
}
export function questionParts(widget:{questions?:WidgetSubquestion[]}):WidgetSubquestion[]{return widget.questions?.length?widget.questions:[]}
/** Phone-only overrides are restricted to geometry and one separately authorized
 * background. Desktop canvas remains authoritative for shared content/styles. */
export type MobilePageLayout={backgroundColor?:string;backgroundAssetId?:string;positions?:Record<string,{x:number;y:number;width:number;height?:number;rotation?:number}>;styles?:Record<string,WidgetTextStyle>};
export function validMobilePageLayout(value:unknown,widgets:unknown):value is MobilePageLayout {
 if(value===null||typeof value!=='object'||Array.isArray(value))return false;
 const m=value as Record<string,unknown>;
 if(Object.keys(m).some(k=>!['backgroundColor','backgroundAssetId','positions','styles'].includes(k)))return false;
 if(m.backgroundColor!==undefined&&(typeof m.backgroundColor!=='string'||!/^#[0-9a-fA-F]{6}$/.test(m.backgroundColor)))return false;
 if(m.backgroundAssetId!==undefined&&(typeof m.backgroundAssetId!=='string'||!uuidRegex.test(m.backgroundAssetId)))return false;
 if(m.styles!==undefined){
  if(!m.styles||typeof m.styles!=='object'||Array.isArray(m.styles))return false;
  const styles=m.styles as Record<string,unknown>,ids=new Set(Array.isArray(widgets)?widgets.map(w=>w?.id):[]);
  if(Object.keys(styles).length>16||Object.keys(styles).some(id=>!ids.has(id)||!validWidgetTextStyle(styles[id])))return false;
 }
 if(m.positions!==undefined){
  if(!m.positions||typeof m.positions!=='object'||Array.isArray(m.positions))return false;
  const positions=m.positions as Record<string,unknown>,ids=new Set(Array.isArray(widgets)?widgets.map(w=>w?.id):[]);
  if(Object.keys(positions).length>16||Object.keys(positions).some(id=>!ids.has(id)||!validWidgetPosition(positions[id])))return false;
 }
 return true;
}
/** Bounded per-element presentation styles. Values are persisted as data, never CSS source. */
type ResultTextStyle={fontFamily?:string;fontSize?:number;color?:string;bold?:boolean;italic?:boolean;underline?:boolean;strikethrough?:boolean};
type ResultTextStyles=Record<string,ResultTextStyle>;
const RESULT_FONTS=['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'] as const;
function validResultTextStyles(value:unknown):value is ResultTextStyles {
 if(value===undefined)return true;
 if(!value||typeof value!=='object'||Array.isArray(value))return false;
 const styles=value as Record<string,unknown>;
 if(Object.keys(styles).length>50)return false;
 return Object.entries(styles).every(([key,item])=>{
  if(!/^(sourceTitle|question:(main|[A-Za-z0-9_-]{1,40})|option:([A-Za-z0-9_-]{1,40}:)?[A-Za-z0-9_-]{1,40}|row:([A-Za-z0-9_-]{1,40}:)?[A-Za-z0-9_-]{1,40})$/.test(key))return false;
  if(!item||typeof item!=='object'||Array.isArray(item))return false;
  const fmt=item as Record<string,unknown>;
  if(Object.keys(fmt).some(name=>!['fontFamily','fontSize','color','bold','italic','underline','strikethrough'].includes(name)))return false;
  return Object.entries(fmt).every(([name,val])=>name==='fontFamily'?RESULT_FONTS.includes(val as any):name==='fontSize'?Number.isInteger(val)&&Number(val)>=8&&Number(val)<=96:name==='color'?typeof val==='string'&&/^#[0-9a-fA-F]{6}$/.test(val):typeof val==='boolean');
 });
}

export type PageDesign={importedImageFit?:'contain'|'cover'|'fill';suppressMaster?:boolean;mobile?:MobilePageLayout;backgroundColor?:string;backgroundAssetId?:string;backgroundUrl?:string;audiencePageId?:string;presenterHidden?:boolean;logos?:string[];header?:string;footer?:string;media?:{kind:'image'|'video'|'pdf';url:string;alt?:string}[];widgets?:{id:string;kind:'rating'|'reactions'|'text'|'divider'|'shape'|'line'|'timer'|'qr'|'profile'|'question'|'postit'|'image'|'video'|'logo'|'pdf'|'topic-question'|'timed-quiz'|'results-button'|'participant-count'|'title'|'footer';label?:string;description?:string;answerMode?:'single'|'multiple'|'text'|'file';options?:{id:string;label:string}[];questions?:WidgetSubquestion[];required?:boolean;durationSeconds?:number;correctOptionId?:string;correctOptionIds?:string[];resultsView?:'bars'|'pie'|'table'|'cloud';style?:WidgetTextStyle;textMarks?:WidgetInlineMark[];position?:{x:number;y:number;width:number;height?:number;rotation?:number};presenterId?:string;showEmail?:boolean;allowAnswerChange?:boolean;autoFit?:boolean;resultsOnly?:boolean;showSourceQuestion?:boolean;showSourceTitle?:boolean;showSourceAnswers?:boolean;showCorrectAnswers?:boolean;pieShowOptionNumbers?:boolean;pieShowPercentages?:boolean;pieSize?:number;barHitGradient?:boolean;barGradientStartColor?:string;barGradientEndColor?:string;resultTextStyles?:Record<string,{fontFamily?:string;fontSize?:number;color?:string;bold?:boolean;italic?:boolean;underline?:boolean;strikethrough?:boolean}>;resultTopCount?:number;resultSortOrder?:'index-asc'|'index-desc'|'count-asc'|'count-desc';showTitle?:boolean;showQrUrl?:boolean;qrUrlFontSize?:number;qrUrlWidthExtra?:number;qrImagePixels?:number;targetKind?:'question'|'quiz'|'session'|'presenter';targetId?:string;targetWidgetId?:string;targetActivityId?:string;targetQuestionId?:string;assetId?:string;crop?:PictureCrop;showNames?:boolean;reactionIconSize?:number;titleFollowPage?:boolean;titleUseMaster?:boolean;footerShowSessionTitle?:boolean;footerShowPageNumber?:boolean;footerSeparator?:boolean;footerSeparatorColor?:string;footerNumberX?:number;footerNumberY?:number}[];master?:{titleStyle?:WidgetTextStyle;widgets?:PageDesign['widgets'];backgroundAssetId?:string}};
export function validPageDesign(x:unknown):x is PageDesign {
 if(x===null||typeof x!=='object'||Array.isArray(x))return false;
 const d=x as Record<string,unknown>;const keys=Object.keys(d);
 if(keys.some(k=>!['importedImageFit','suppressMaster','backgroundColor','backgroundAssetId','backgroundUrl','audiencePageId','presenterHidden','logos','header','footer','media','widgets','master','mobile'].includes(k)))return false;
 if(d.mobile!==undefined&&!validMobilePageLayout(d.mobile,d.widgets))return false;
 if(d.master!==undefined){
  if(!d.master||typeof d.master!=='object'||Array.isArray(d.master))return false;
  const master=d.master as Record<string,unknown>;
  if(Object.keys(master).some(k=>!['titleStyle','widgets','backgroundAssetId'].includes(k))||!validWidgetTextStyle(master.titleStyle)||(master.backgroundAssetId!==undefined&&(typeof master.backgroundAssetId!=='string'||!uuidRegex.test(master.backgroundAssetId))))return false;
  if(master.widgets!==undefined){
   const widgets=master.widgets;
   if(!Array.isArray(widgets)||widgets.length>16||
      ['title','footer'].some(kind=>widgets.filter((w:any)=>w?.kind===kind).length>1)||
      !validPageDesign({widgets}))return false;
  }
 }
 const url=(v:unknown)=>typeof v==='string'&&v.length<=1024&&/^https:\/\/[^\s]+$/.test(v);
 if(d.importedImageFit!==undefined&&!['contain','cover','fill'].includes(d.importedImageFit as string))return false;
 if(d.suppressMaster!==undefined&&typeof d.suppressMaster!=='boolean')return false;
 if(d.importedImageFit!==undefined&&!d.backgroundAssetId)return false;
 if(d.backgroundColor!==undefined&&(typeof d.backgroundColor!=='string'||!/^#[0-9a-fA-F]{6}$/.test(d.backgroundColor)))return false;
 if(d.backgroundAssetId!==undefined&&(typeof d.backgroundAssetId!=='string'||!uuidRegex.test(d.backgroundAssetId)))return false;
 if(d.backgroundUrl!==undefined&&!url(d.backgroundUrl))return false;
 if(d.audiencePageId!==undefined&&(typeof d.audiencePageId!=='string'||!uuidRegex.test(d.audiencePageId)))return false;
 if(d.presenterHidden!==undefined&&typeof d.presenterHidden!=='boolean')return false;
 if(d.logos!==undefined&&(!Array.isArray(d.logos)||d.logos.length>5||!d.logos.every(url)))return false;
 for(const key of ['header','footer'])if(d[key]!==undefined&&(typeof d[key]!=='string'||d[key].length>500))return false;
 if(d.media!==undefined&&(!Array.isArray(d.media)||d.media.length>8||!d.media.every((m:any)=>m&&['image','video','pdf'].includes(m.kind)&&url(m.url)&&(m.alt===undefined||(typeof m.alt==='string'&&m.alt.length<=240)))))return false;
 if(d.widgets!==undefined&&(!Array.isArray(d.widgets)||d.widgets.length>16||new Set(d.widgets.map((w:any)=>w?.id)).size!==d.widgets.length||!d.widgets.every((w:any)=>w&&typeof w.id==='string'&&/^[a-zA-Z0-9_-]{1,48}$/.test(w.id)&&['rating','reactions','text','divider','shape','line','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count','title','footer'].includes(w.kind)&&(w.kind!=='rating'||typeof w.label==='string'&&w.label.trim().length>0)&&(w.description===undefined||(typeof w.description==='string'&&w.description.length<=500))&&(w.answerMode===undefined||validAnswerMode(w.answerMode))&&(w.options===undefined||(Array.isArray(w.options)&&w.options.length<=12&&w.options.every((o:any)=>typeof o?.id==='string'&&/^[a-zA-Z0-9_-]{1,40}$/.test(o.id)&&typeof o?.label==='string'&&o.label.trim().length>0&&o.label.length<=255)&&new Set(w.options.map((o:any)=>o.id)).size===w.options.length))&&validWidgetSubquestions(w.questions,w.kind)&&(w.required===undefined||typeof w.required==='boolean')&&(w.resultsView===undefined||['bars','pie','table','cloud'].includes(w.resultsView))&&(w.titleFollowPage===undefined||(w.kind==='title'&&typeof w.titleFollowPage==='boolean'))&&(w.titleUseMaster===undefined||(w.kind==='title'&&typeof w.titleUseMaster==='boolean'))&&(w.footerShowSessionTitle===undefined||(w.kind==='footer'&&typeof w.footerShowSessionTitle==='boolean'))&&(w.footerShowPageNumber===undefined||(w.kind==='footer'&&typeof w.footerShowPageNumber==='boolean'))&&(w.footerSeparator===undefined||(w.kind==='footer'&&typeof w.footerSeparator==='boolean'))&&(w.footerSeparatorColor===undefined||(w.kind==='footer'&&typeof w.footerSeparatorColor==='string'&&/^#[0-9A-Fa-f]{6}$/.test(w.footerSeparatorColor)))&&(w.footerNumberX===undefined||(w.kind==='footer'&&typeof w.footerNumberX==='number'&&Number.isFinite(w.footerNumberX)&&w.footerNumberX>=0&&w.footerNumberX<=100))&&(w.footerNumberY===undefined||(w.kind==='footer'&&typeof w.footerNumberY==='number'&&Number.isFinite(w.footerNumberY)&&w.footerNumberY>=0&&w.footerNumberY<=100))&&(w.showNames===undefined||typeof w.showNames==='boolean')&&(w.reactionIconSize===undefined||(w.kind==='reactions'&&Number.isInteger(w.reactionIconSize)&&w.reactionIconSize>=16&&w.reactionIconSize<=96))&&(w.showEmail===undefined||(w.kind==='profile'&&typeof w.showEmail==='boolean'))&&(w.allowAnswerChange===undefined||(['question','timed-quiz'].includes(w.kind)&&typeof w.allowAnswerChange==='boolean'))&&(w.autoFit===undefined||typeof w.autoFit==='boolean')&&(w.resultsOnly===undefined||(w.kind==='results-button'&&typeof w.resultsOnly==='boolean'))&&(w.showSourceQuestion===undefined||(w.kind==='results-button'&&typeof w.showSourceQuestion==='boolean'))&&(w.showSourceTitle===undefined||(w.kind==='results-button'&&typeof w.showSourceTitle==='boolean'))&&(w.showSourceAnswers===undefined||(w.kind==='results-button'&&typeof w.showSourceAnswers==='boolean'))&&(w.showCorrectAnswers===undefined||(w.kind==='results-button'&&typeof w.showCorrectAnswers==='boolean'))&&(w.pieSize===undefined||(w.kind==='results-button'&&Number.isInteger(w.pieSize)&&w.pieSize>=25&&w.pieSize<=150))&&(['pieShowOptionNumbers','pieShowPercentages','barHitGradient'].every(k=>w[k]===undefined||(w.kind==='results-button'&&typeof w[k]==='boolean')))&&(['barGradientStartColor','barGradientEndColor'].every(k=>w[k]===undefined||(w.kind==='results-button'&&typeof w[k]==='string'&&/^#[0-9a-fA-F]{6}$/.test(w[k]))))&&(w.resultTextStyles===undefined||(w.kind==='results-button'&&validResultTextStyles(w.resultTextStyles)))&&(w.resultTopCount===undefined||(w.kind==='results-button'&&Number.isInteger(w.resultTopCount)&&w.resultTopCount>=1&&w.resultTopCount<=20))&&(w.resultSortOrder===undefined||(w.kind==='results-button'&&['index-asc','index-desc','count-asc','count-desc'].includes(w.resultSortOrder)))&&(w.showTitle===undefined||typeof w.showTitle==='boolean')&&(w.showQrUrl===undefined||(w.kind==='qr'&&typeof w.showQrUrl==='boolean'))&&(w.qrUrlFontSize===undefined||(w.kind==='qr'&&Number.isInteger(w.qrUrlFontSize)&&w.qrUrlFontSize>=10&&w.qrUrlFontSize<=96))&&(w.qrUrlWidthExtra===undefined||(w.kind==='qr'&&typeof w.qrUrlWidthExtra==='number'&&Number.isFinite(w.qrUrlWidthExtra)&&w.qrUrlWidthExtra>=0&&w.qrUrlWidthExtra<=1280))&&(w.qrImagePixels===undefined||(w.kind==='qr'&&Number.isFinite(w.qrImagePixels)&&w.qrImagePixels>=16&&w.qrImagePixels<=4096))&&(w.durationSeconds===undefined||(Number.isInteger(w.durationSeconds)&&(w.kind==='timer'?w.durationSeconds>=1&&w.durationSeconds<=3600:w.durationSeconds>=5&&w.durationSeconds<=600)))&&(w.answerKeyEnabled===undefined||(['question','timed-quiz'].includes(w.kind)&&typeof w.answerKeyEnabled==='boolean'))&&(w.answerKeyEnabled!==true||(['single','multiple'].includes(w.answerMode||(w.kind==='timed-quiz'?'single':'text'))&& (w.answerMode!=='single'||!Array.isArray(w.correctOptionIds)||w.correctOptionIds.length<=1)))&&(w.correctOptionId===undefined||typeof w.correctOptionId==='string')&&(w.correctOptionIds===undefined||(Array.isArray(w.correctOptionIds)&&w.correctOptionIds.every((id:any)=>typeof id==='string')))&&validWidgetTextStyle(w.style)&&validWidgetInlineMarks(w.textMarks)&&(w.textMarks===undefined||w.textMarks.every((mark:any)=>{const field=mark.field as string;const value=field==='label'?w.label:field==='description'?w.description:w.options?.find((option:any)=>'option:'+option.id===field)?.label ?? (field.startsWith('question:') ? (()=>{const parts=field.split(':');const q=w.questions?.find((item:any)=>item.id===parts[1]);return parts[2]==='label'?q?.label:parts[2]==='description'?q?.description:parts[2]==='option'?q?.options?.find((o:any)=>o.id===parts[3])?.label:undefined})() : undefined);return typeof value==='string'&&mark.end<=value.length}))&&(w.position===undefined||validWidgetPosition(w.position))&&(w.label===undefined||(typeof w.label==='string'&&w.label.length<=240))&&(w.presenterId===undefined||(typeof w.presenterId==='string'&&uuidRegex.test(w.presenterId)))&&(w.targetKind===undefined||['question','quiz','session','presenter'].includes(w.targetKind))&&(w.targetId===undefined||(typeof w.targetId==='string'&&uuidRegex.test(w.targetId)))&&(w.targetWidgetId===undefined||(w.kind==='results-button'&&typeof w.targetWidgetId==='string'&&/^[a-zA-Z0-9_-]{1,48}$/.test(w.targetWidgetId)))&&(w.targetActivityId===undefined||(w.kind==='results-button'&&typeof w.targetActivityId==='string'&&uuidRegex.test(w.targetActivityId)))&&(w.targetQuestionId===undefined||(w.kind==='results-button'&&typeof w.targetQuestionId==='string'&&/^[a-zA-Z0-9_-]{1,40}$/.test(w.targetQuestionId)))&&(w.assetId===undefined||(typeof w.assetId==='string'&&uuidRegex.test(w.assetId)))&&(w.crop===undefined||(['image','logo'].includes(w.kind)&&validPictureCrop(w.crop)))&&(!['image','video','logo','pdf'].includes(w.kind)||(typeof w.assetId==='string'&&uuidRegex.test(w.assetId))))))return false;
 // On-page result widgets must reference valid local sources; cross-page
 // references are verified against the session in the authenticated save route.
 if(Array.isArray(d.widgets))for(const widget of d.widgets){
  if(widget.kind!=='results-button'||widget.targetWidgetId===undefined)continue;
  if(widget.targetActivityId)continue;
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
