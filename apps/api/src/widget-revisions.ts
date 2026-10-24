/** Compare answer semantics rather than historic storage representations. */
export function widgetAnswerShapeChanged(old:any,next:any):boolean {
 const normalize=(w:any)=>{
  const timed=w.kind==='timed-quiz';
  const mode=timed?(w.answerMode==='multiple'?'multiple':'single'):(w.answerMode||'text');
  const options=w.options||[];
  const base:any={answerMode:mode,required:w.required!==false,options};
  if(timed){
   base.durationSeconds=w.durationSeconds??30;
   // Match the scorer's precedence: the legacy single-answer key wins over
   // an empty or stale array, while multiple-answer quizzes use the array.
   if(mode==='multiple')base.correctOptionIds=Array.isArray(w.correctOptionIds)?w.correctOptionIds:[];
   else base.correctOptionIds=typeof w.correctOptionId==='string'&&w.correctOptionId
    ?[w.correctOptionId]
    :Array.isArray(w.correctOptionIds)&&w.correctOptionIds.length===1?w.correctOptionIds:[];
  }
  return JSON.stringify(base);
 };
 return normalize(old)!==normalize(next);
}
export function aggregateWidgetAnswerRevisions(rows:{revision:number;answer_mode:string;answer_payload:{optionIds?:string[];text?:string|null;assetId?:string|null}}[]){
 type Stats={revision:number;responses:number;options:Record<string,number>;texts:number;attachments:number};
 const revisions=new Map<number,Stats>();
 for(const row of rows){
  const k=Number(row.revision);
  // Historical or imported corrupt revisions must not create NaN or fractional
  // keys in the public response. All stored revisions start at one.
  if(!Number.isSafeInteger(k)||k<1)continue;
  let val=revisions.get(k);
  if(!val){val={revision:k,responses:0,options:{},texts:0,attachments:0};revisions.set(k,val)}
  val.responses++;
  const payload=row.answer_payload;
  const selected=Array.isArray(payload?.optionIds)?payload.optionIds:[];
  for(const option of new Set(selected)){
   if(typeof option!=='string'||!/^[a-zA-Z0-9_-]{1,40}$/.test(option))continue;
   // Define an own, enumerable property so reserved names cannot resolve to
   // Object.prototype and the JSON response retains an ordinary object shape.
   const current=Object.hasOwn(val.options,option)?val.options[option]:0;
   Object.defineProperty(val.options,option,{value:current+1,enumerable:true,writable:true,configurable:true});
  }
  if(typeof payload?.text==='string'&&payload.text.length>0)val.texts++;
  if(typeof payload?.assetId==='string'&&payload.assetId.length>0)val.attachments++;
 }
 return [...revisions.values()].sort((a,b)=>a.revision-b.revision);
}

/** Prevent changing the answer key or duration of a live timed quiz. Pure geometry and styling are safe. */
export function liveTimedWidgetMutation(previous:any[],next:any[]):boolean {
 // Duplicate IDs make answer attribution ambiguous. Reject them before building
 // the lookup map, which would otherwise silently discard earlier entries.
 const ids=new Set<string>();
 for(const widget of next){
  if(typeof widget?.id!=='string'||!widget.id||ids.has(widget.id))return true;
  ids.add(widget.id);
 }
 const newWidgets=new Map(next.filter(w=>w.kind==='timed-quiz').map(w=>[w.id,w]));
 return previous.some(old=>old.kind==='timed-quiz'&&(!newWidgets.has(old.id)||widgetAnswerShapeChanged(old,newWidgets.get(old.id))));
}
