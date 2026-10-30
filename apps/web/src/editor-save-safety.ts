/** Keep new selection-mode questions immediately editable and saveable. */
export function questionModeOptions(existing:{id:string;label:string}[],mode:string):{id:string;label:string}[]{
 if(!['single','multiple'].includes(mode))return existing;
 if(existing.length>=2)return existing;
 const ids=new Set(existing.map(o=>o.id));
 const result=[...existing];
 for(const option of [{id:'choice_a',label:'Opzione A'},{id:'choice_b',label:'Opzione B'}]){
  if(result.length>=2)break;
  let id=option.id;
  for(let n=1;ids.has(id);n++)id=option.id+'_'+n;
  result.push({id,label:option.label});ids.add(id);
 }
 return result;
}
/** Explain the most frequent authoring mistake without leaking any private data. */
export function invalidPageWidgetReason(design:{widgets?:any[]}):string|undefined{
 for(const w of design.widgets||[]){
  if(!['question','timed-quiz'].includes(w.kind))continue;
  const options=Array.isArray(w.options)?w.options:[];
  if(['single','multiple'].includes(w.answerMode)&&options.length<2)return 'Il sondaggio richiede almeno due opzioni di risposta.';
  if(options.some((o:any)=>!o.label?.trim()))return 'Ogni opzione di risposta deve contenere un testo.';
  if((Array.isArray(w.questions)?w.questions:[]).some((q:any)=>['single','multiple'].includes(q.answerMode)&&(!Array.isArray(q.options)||q.options.length<2)))return 'Una domanda indipendente richiede almeno due opzioni di risposta.';
 }
 return undefined;
}
