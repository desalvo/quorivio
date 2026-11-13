/** Page-scoped presenter statistics; result controls never reference participants directly. */
export const STATISTICAL_WIDGET_KINDS=['question','timed-quiz','rating','reactions','topic-question'] as const;
export type StatisticalWidget={id:string;kind:string;label?:string;description?:string;answerMode?:string;options?:{id:string;label:string}[];targetWidgetId?:string;targetActivityId?:string;targetQuestionId?:string;questions?:{id:string;label:string;description?:string;answerMode?:string;options?:{id:string;label:string}[]}[];resultsView?:string;gaugeMinMode?:'auto'|'manual';gaugeMaxMode?:'auto'|'manual';gaugeMin?:number;gaugeMax?:number;gaugeGradient?:boolean;gaugeMinColor?:string;gaugeMaxColor?:string;gaugeColor?:string;gaugeShowValue?:boolean;gaugeAggregation?:'min'|'max'|'mean';gaugeTransparent?:boolean;bubbleNoScroll?:boolean;resultSortOrder?:'index-asc'|'index-desc'|'count-asc'|'count-desc';resultsOnly?:boolean;showTitle?:boolean;showSourceQuestion?:boolean;showSourceTitle?:boolean;showSourceAnswers?:boolean;showResponseParticipation?:boolean;responseParticipationGaugeSize?:number};
export type StatRow={id:string;label:string;count:number};
export type SourceQuestionPart={id?:string;label:string;description?:string;answerMode?:string;options?:{id:string;label:string}[]};
/** The author may reveal a read-only copy of the SOURCE question above the
 * aggregated results. Never infer grading keys or send the source to viewers. */
export function resultSourceTitleVisible(result:Pick<StatisticalWidget,'showSourceQuestion'|'showSourceTitle'>):boolean {return result.showSourceTitle??result.showSourceQuestion===true;}
export function resultSourceAnswersVisible(result:Pick<StatisticalWidget,'showSourceQuestion'|'showSourceAnswers'>):boolean {return result.showSourceAnswers??result.showSourceQuestion===true;}
export function linkedResultQuestion(result:StatisticalWidget,source:StatisticalWidget):{part:SourceQuestionPart;questionId:string}|undefined{
 if(result.showSourceQuestion!==true&&result.showSourceTitle!==true&&result.showSourceAnswers!==true)return undefined;
 if(!resultSourceTitleVisible(result)&&!resultSourceAnswersVisible(result))return undefined;
 const questionId=result.targetQuestionId||'';
 const part=questionId?source.questions?.find(q=>q.id===questionId):source;
 if(!part)return undefined;
 return {part:{id:questionId||undefined,label:part.label||'',description:part.description,answerMode:part.answerMode,options:part.options},questionId};
}

export function eligibleStatisticSources(widgets:StatisticalWidget[],excluding?:string):StatisticalWidget[]{
 return widgets.filter(w=>w.id!==excluding&&(STATISTICAL_WIDGET_KINDS as readonly string[]).includes(w.kind));
}
export function linkedStatisticSource(widget:StatisticalWidget,widgets:StatisticalWidget[]):StatisticalWidget|undefined{
 return eligibleStatisticSources(widgets,widget.id).find(w=>w.id===widget.targetWidgetId);
}
/** Strictly resolve results against an activity from the same authenticated
 * owner snapshot. No public participant snapshot contains other pages. */
export function linkedStatisticActivity<T extends {id:string;page_design?:{widgets?:StatisticalWidget[]}}>(widget:StatisticalWidget,current:T,activities:readonly T[]):T|undefined{
 return widget.targetActivityId?activities.find(activity=>activity.id===widget.targetActivityId):current;
}
/** Unified result source for real presenter projection and both rehearsal
 * panes. The activity id is ALWAYS the source activity id, not the current
 * presenter page id; its widgets supply the option labels and chart format. */
export function linkedStatisticContext<T extends {id:string;page_design?:{widgets?:StatisticalWidget[]}}>(
 widget:StatisticalWidget,current:T,activities:readonly T[],localWidgets?:StatisticalWidget[]
):{activity:T;widgets:StatisticalWidget[];source:StatisticalWidget}|undefined{
 const activity=linkedStatisticActivity(widget,current,activities);
 if(!activity)return undefined;
 const widgets=(activity.id===current.id&&localWidgets)||activity.page_design?.widgets||[];
 const source=linkedStatisticSource(widget,widgets);
 return source?{activity,widgets,source}:undefined;
}
export type ResultView='bars'|'pie'|'table'|'cloud'|'gauge'|'bubbles';
/** Explicit result view overrides source; legacy results inherit the source view. */
export function effectiveResultView(resultWidget:StatisticalWidget,widgets:StatisticalWidget[]):ResultView{
 const source=linkedStatisticSource(resultWidget,widgets);
 if(!source)return 'bars';
 const view=resultWidget.resultsView??source.resultsView??(source.kind==='reactions'?'bubbles':'bars');
 // A reaction-only bubble mode cannot leak into a re-linked non-reaction source.
 if(view==='bubbles')return source.kind==='reactions'?'bubbles':'bars';
 return view==='pie'||view==='table'||view==='cloud'||view==='gauge'?view:'bars';
}
/** Reaction-specific, anonymous aggregate bubble sizing; no user identities. */
export function reactionBubbles(rows:readonly StatRow[],limit=5,sort:'count-desc'|'count-asc'|'index-asc'|'index-desc'='count-desc'){
 const available=rows.filter(r=>Number.isSafeInteger(r.count)&&r.count>=0);
 const total=available.reduce((sum,r)=>sum+r.count,0);
 const max=Math.max(1,...available.map(r=>r.count));
 const safeLimit=Number.isSafeInteger(limit)&&limit>=1&&limit<=20?limit:5;
 const ranked=available.map((row,index)=>({row,index})).sort((a,b)=>sort==='index-asc'?a.index-b.index:sort==='index-desc'?b.index-a.index:sort==='count-asc'?a.row.count-b.row.count||a.index-b.index:b.row.count-a.row.count||a.index-b.index);
 return ranked.slice(0,safeLimit).map(({row})=>({
  ...row,percent:total>0?row.count/total*100:0,
  size:Math.round(56+60*Math.sqrt(Math.max(0,row.count)/max))
 }));
}

/** Arrange anonymous emoji results inside a resizeable chart frame, with no scroll.
 * All measurements refer to the chart's actual content box, not window size. */
export function fitReactionBubbleLayout(items:readonly {size:number}[],width:number,height:number){
 const count=Math.max(1,items.length);
 const W=Math.max(1,Number.isFinite(width)?width:1),H=Math.max(1,Number.isFinite(height)?height:1);
 const gap=Math.max(1,Math.min(8,Math.floor(Math.min(W,H)/85)));
 const padding=Math.max(1,Math.min(5,Math.floor(Math.min(W,H)/60)));
 let best={columns:1,rows:count,diameter:0,cellWidth:W,cellHeight:H};
 for(let columns=1;columns<=count;columns++){
  const rows=Math.ceil(count/columns);
  const cellWidth=Math.max(1,(W-2*padding-gap*(columns-1))/columns);
  const cellHeight=Math.max(1,(H-2*padding-gap*(rows-1))/rows);
  const metaHeight=Math.min(34,Math.max(6,cellHeight*.32));
  const diameter=Math.max(1,Math.min(136,cellWidth-2,cellHeight-metaHeight-2));
  if(diameter>best.diameter)best={columns,rows,diameter,cellWidth,cellHeight};
 }
 const maxSourceSize=Math.max(1,...items.map(item=>Number.isFinite(item.size)?Math.max(0,item.size):0));
 const diameters=items.map(item=>Math.max(1,Math.floor(best.diameter*(.58+.42*Math.max(0,Math.min(1,item.size/maxSourceSize))))));
 const metaFont=Math.max(2,Math.min(15,(best.cellHeight-best.diameter)/2.7,best.cellHeight*.145));
 return {...best,diameters,gap,padding,metaFont,emojiFont:Math.max(2,Math.min(50,best.diameter*.44))};
}

export type GaugeConfig={
 gaugeMinMode?:'auto'|'manual';gaugeMaxMode?:'auto'|'manual';gaugeMin?:number;gaugeMax?:number;
 gaugeAggregation?:'min'|'max'|'mean';gaugeGradient?:boolean;gaugeMinColor?:string;
 gaugeMaxColor?:string;gaugeColor?:string;gaugeShowValue?:boolean;
};
export type GaugeModel={value:number|null;min:number;max:number;percent:number;total:number;aggregation:'min'|'max'|'mean'};
/** Work on anonymous presenter-only histogram counts; rating scores use weighted votes. */
export function gaugeModel(rows:readonly StatRow[],config:GaugeConfig={},sourceKind='question'):GaugeModel{
 const bins=rows.filter(r=>Number.isSafeInteger(r.count)&&r.count>0);
 // Treat localized decimal scores as numeric, but never coerce blank, hex or exponent labels.
 // A non-numeric category continues to represent its response count instead.
 const scored=bins.map(r=>{const label=r.label.trim();return {n:/^[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)$/.test(label)?Number(label.replace(',','.')):NaN,count:r.count};});
 const numeric=scored.length>0&&scored.every(r=>Number.isFinite(r.n));
 const samples=numeric?scored:bins.map(r=>({n:r.count,count:1}));
 const aggregation=config.gaugeAggregation==='min'||config.gaugeAggregation==='max'?config.gaugeAggregation:'mean';
 const raw=samples.length?(aggregation==='min'?Math.min(...samples.map(r=>r.n)):aggregation==='max'?Math.max(...samples.map(r=>r.n)):samples.reduce((sum,r)=>sum+r.n*r.count,0)/samples.reduce((sum,r)=>sum+r.count,0)):null;
 const autoMin=sourceKind==='rating'?0:samples.length?Math.min(0,...samples.map(r=>r.n)):0;
 const autoMax=sourceKind==='rating'?9:samples.length?Math.max(1,...samples.map(r=>r.n)):100;
 const finite=(n:unknown):n is number=>typeof n==='number'&&Number.isFinite(n)&&n>=-1000000&&n<=1000000;
 const min=config.gaugeMinMode==='manual'&&finite(config.gaugeMin)?config.gaugeMin:autoMin;
 const candidateMax=config.gaugeMaxMode==='manual'&&finite(config.gaugeMax)?config.gaugeMax:autoMax;
 const max=candidateMax>min?candidateMax:min+1;
 const percent=raw===null?0:Math.min(100,Math.max(0,(raw-min)/(max-min)*100));
 return {value:raw,min,max,percent,total:bins.reduce((sum,r)=>sum+r.count,0),aggregation};
}
export function gaugeColor(input:unknown,fallback='#000000'):string{
 return typeof input==='string'&&/^#[0-9a-fA-F]{6}$/.test(input)?input:fallback;
}
export const REHEARSAL_EMOJIS=['👍','❤️','😂','😮','👏','🎉','🤔','😕'] as const;
/** The same safe, count-only projection is used by live PostgreSQL and by rehearsal.
 * The presenter may see counts; participants never receive result-widget data. */
export function topicQuestionRows(value:unknown):StatRow[]{
 const count=typeof value==='number'&&Number.isSafeInteger(value)&&value>=0?value:0;
 return [{id:'topic-count',label:'Domande ricevute',count}];
}

/** Stable per preview opening and per source; fresh preview openings have different seed. */
export function sampleStatisticRows(source:StatisticalWidget,seed:number,choices:Record<string,string|string[]>={},questionId='',topicSubmissions:Record<string,number>={}):StatRow[]{
 const part=questionId?source.questions?.find(q=>q.id===questionId):source;
 if(!part)return [];
 const options=source.kind==='rating'?Array.from({length:10},(_,n)=>({id:String(n),label:String(n)})):
 source.kind==='reactions'?REHEARSAL_EMOJIS.map(emoji=>({id:emoji,label:emoji})):
 (part.options?.length?part.options:[{id:'yes',label:'Sì'},{id:'no',label:'No'}]);
 let value=seed>>>0;
 for(const char of source.id+questionId)value=(Math.imul(value^char.charCodeAt(0),16777619))>>>0;
 const selected=choices[questionId?source.id+':'+questionId:source.id];
 if(source.kind==='topic-question'){
  const added=topicSubmissions[source.id];
  return topicQuestionRows(2+(value%22)+(Number.isSafeInteger(added)&&added>0?added:0));
 }
 return options.map((o,i)=>{
  value=(Math.imul(value^i,1664525)+1013904223)>>>0;
  const picked=Array.isArray(selected)?selected.includes(o.id):selected===o.id;
  return {id:o.id,label:o.label,count:2+(value%22)+(picked?1:0)};
 });
}
export function rowsFromWidgetAnswerDetail(source:StatisticalWidget,data:any,questionId=''):StatRow[]{
 const part=questionId?source.questions?.find(q=>q.id===questionId):source;
 if(!part)return [];
 const counts=new Map<string,number>();
 for(const rev of data?.revisions||[])for(const [id,count] of Object.entries(rev.options||{}))counts.set(id,(counts.get(id)||0)+Number(count));
 if((part.answerMode==='text'||(!part.answerMode&&!part.options?.length))&&source.kind==='question'){
  const aggregate=Array.isArray(data?.text_counts)?data.text_counts:[];
  const shortRows:StatRow[]=aggregate.filter((x:any)=>typeof x.word==='string'&&x.word.length<=48&&Number.isSafeInteger(x.count)&&x.count>0).slice(0,100).map((x:any)=>({id:'text:'+x.word,label:x.word,count:x.count}));
  if(shortRows.length)return shortRows;
  const total=(data?.revisions||[]).reduce((sum:number,revision:any)=>sum+(Number(revision.texts)||0),0);
  return total>0?[{id:'total-text',label:'Risposte testuali',count:total}]:[];
 }
 return (part.options||[]).map(o=>({id:o.id,label:o.label,count:counts.get(o.id)||0}));
}

/** Local rehearsal text answers, presenter-only. Keep authored text distinct from
 * generated samples: no trial response is ever persisted or sent over the network. */
export function rehearsalFreeTextRows(source:StatisticalWidget,answers:Record<string,string|string[]>,questionId=''):StatRow[]{
 const part=questionId?source.questions?.find(q=>q.id===questionId):source;
 if(source.kind!=='question'||(part?.answerMode||'text')!=='text')return [];
 const key=source.id+(questionId?':'+questionId:'');
 const answer=answers[key];
 return [{id:'fixture-a',label:'Risposta dimostrativa A',count:2},{id:'fixture-b',label:'Risposta dimostrativa B',count:1},...(typeof answer==='string'&&answer.trim()?[{id:'authored-response',label:answer.trim().slice(0,5000),count:1}]:[])];
}
