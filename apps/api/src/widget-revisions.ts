export function widgetAnswerShapeChanged(old:any,next:any):boolean {
 const normalize=(w:any)=>JSON.stringify({answerMode:w.answerMode||'text',required:w.required!==false,options:w.options||[],...(w.kind==='timed-quiz'?{durationSeconds:w.durationSeconds??30,correctOptionIds:w.correctOptionIds||[],correctOptionId:w.correctOptionId||null}:{})});
 return normalize(old)!==normalize(next);
}
export function aggregateWidgetAnswerRevisions(rows:{revision:number;answer_mode:string;answer_payload:{optionIds?:string[];text?:string|null;assetId?:string|null}}[]){
 const revisions=new Map<number,{revision:number;responses:number;options:Record<string,number>;texts:number;attachments:number}>();
 for(const row of rows){const k=Number(row.revision);const val=revisions.get(k)||{revision:k,responses:0,options:{} as Record<string,number>,texts:0,attachments:0};val.responses++;for(const o of row.answer_payload?.optionIds||[])val.options[o]=(val.options[o]||0)+1;if(row.answer_payload?.text)val.texts++;if(row.answer_payload?.assetId)val.attachments++;revisions.set(k,val)}
 return [...revisions.values()].sort((a,b)=>a.revision-b.revision);
}

/** Prevent changing the answer key or duration of a live timed quiz. Pure geometry and styling are safe. */
export function liveTimedWidgetMutation(previous:any[],next:any[]):boolean {
 const newWidgets=new Map(next.filter(w=>w.kind==='timed-quiz').map(w=>[w.id,w]));
 return previous.some(old=>old.kind==='timed-quiz'&&(!newWidgets.has(old.id)||widgetAnswerShapeChanged(old,newWidgets.get(old.id))));
}
