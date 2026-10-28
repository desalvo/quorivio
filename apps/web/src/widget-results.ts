/** Page-scoped presenter statistics; result controls never reference participants directly. */
export const STATISTICAL_WIDGET_KINDS=['question','timed-quiz','rating','reactions'] as const;
export type StatisticalWidget={id:string;kind:string;label?:string;options?:{id:string;label:string}[];targetWidgetId?:string;targetQuestionId?:string;questions?:{id:string;label:string;options?:{id:string;label:string}[]}[];resultsView?:string};
export type StatRow={id:string;label:string;count:number};
export function eligibleStatisticSources(widgets:StatisticalWidget[],excluding?:string):StatisticalWidget[]{
 return widgets.filter(w=>w.id!==excluding&&(STATISTICAL_WIDGET_KINDS as readonly string[]).includes(w.kind));
}
export function linkedStatisticSource(widget:StatisticalWidget,widgets:StatisticalWidget[]):StatisticalWidget|undefined{
 return eligibleStatisticSources(widgets,widget.id).find(w=>w.id===widget.targetWidgetId);
}
export const REHEARSAL_EMOJIS=['👍','❤️','😂','😮','👏','🎉','🤔','😕'] as const;
/** Stable per preview opening and per source; fresh preview openings have different seed. */
export function sampleStatisticRows(source:StatisticalWidget,seed:number,choices:Record<string,string|string[]>={},questionId=''):StatRow[]{
 const part=questionId?source.questions?.find(q=>q.id===questionId):source;
 if(!part)return [];
 const options=source.kind==='rating'?Array.from({length:11},(_,n)=>({id:String(n),label:String(n)})):
 source.kind==='reactions'?REHEARSAL_EMOJIS.map(emoji=>({id:emoji,label:emoji})):
 (part.options?.length?part.options:[{id:'yes',label:'Sì'},{id:'no',label:'No'}]);
 let value=seed>>>0;
 for(const char of source.id+questionId)value=(Math.imul(value^char.charCodeAt(0),16777619))>>>0;
 const selected=choices[questionId?source.id+':'+questionId:source.id];
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
