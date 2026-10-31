/** Page-scoped presenter statistics; result controls never reference participants directly. */
export const STATISTICAL_WIDGET_KINDS=['question','timed-quiz','rating','reactions','topic-question'] as const;
export type StatisticalWidget={id:string;kind:string;label?:string;options?:{id:string;label:string}[];targetWidgetId?:string;targetQuestionId?:string;questions?:{id:string;label:string;options?:{id:string;label:string}[]}[];resultsView?:string};
export type StatRow={id:string;label:string;count:number};
export function eligibleStatisticSources(widgets:StatisticalWidget[],excluding?:string):StatisticalWidget[]{
 return widgets.filter(w=>w.id!==excluding&&(STATISTICAL_WIDGET_KINDS as readonly string[]).includes(w.kind));
}
export function linkedStatisticSource(widget:StatisticalWidget,widgets:StatisticalWidget[]):StatisticalWidget|undefined{
 return eligibleStatisticSources(widgets,widget.id).find(w=>w.id===widget.targetWidgetId);
}
export type ResultView='bars'|'pie'|'table'|'cloud';
/** The source question/quiz/poll controls the appearance; result widgets cannot override it. */
export function effectiveResultView(resultWidget:StatisticalWidget,widgets:StatisticalWidget[]):ResultView{
 const view=linkedStatisticSource(resultWidget,widgets)?.resultsView;
 return view==='pie'||view==='table'||view==='cloud'?view:'bars';
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
 const options=source.kind==='rating'?Array.from({length:11},(_,n)=>({id:String(n),label:String(n)})):
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
 return (part.options||[]).map(o=>({id:o.id,label:o.label,count:counts.get(o.id)||0}));
}

/** Local rehearsal text answers, presenter-only. Keep authored text distinct from
 * generated samples: no trial response is ever persisted or sent over the network. */
export function rehearsalFreeTextRows(source:StatisticalWidget&{answerMode?:string;questions?:any[]},answers:Record<string,string|string[]>,questionId=''):StatRow[]{
 const part=questionId?source.questions?.find(q=>q.id===questionId):source;
 if(source.kind!=='question'||(part?.answerMode||'text')!=='text')return [];
 const key=source.id+(questionId?':'+questionId:'');
 const answer=answers[key];
 return [{id:'fixture-a',label:'Risposta dimostrativa A',count:2},{id:'fixture-b',label:'Risposta dimostrativa B',count:1},...(typeof answer==='string'&&answer.trim()?[{id:'authored-response',label:answer.trim().slice(0,5000),count:1}]:[])];
}
