import React from 'react';
import {RESULT_FONTS,resultElementKey,type ResultTextStyles,type ResultTextStyle} from './result-text-style.js';
/** Independent, persisted formatting for each linked question/option/result label. */
export function ResultFormatControls({source,questionId='',styles={},onChange}:{source:any;questionId?:string;styles?:ResultTextStyles;onChange:(value:ResultTextStyles)=>void}){
 if(!source)return <span>Collega prima una widget sorgente.</span>;
 const part=questionId?source.questions?.find((q:any)=>q.id===questionId):source;
 const fields=[{key:'sourceTitle',label:'Titolo widget collegata'},...(part?[{key:`question:${questionId||'main'}`,label:'Testo della domanda'},...(part.options||[]).map((o:any)=>({key:resultElementKey('option',questionId,o.id),label:`Opzione: ${o.label}`})),...(part.options||[]).map((o:any)=>({key:resultElementKey('row',questionId,o.id),label:`Risultato: ${o.label}`}))]:[])];
 const update=(key:string,delta:Partial<ResultTextStyle>)=>onChange({...styles,[key]:{...styles[key],...delta}});
 return <div className="result-format-fields">{fields.map(item=>{const fmt=styles[item.key]||{};return <fieldset key={item.key} className="result-format-field"><legend>{item.label}</legend>
  <label>Font <select aria-label={'Font '+item.label} value={fmt.fontFamily||'Arial'} onChange={e=>update(item.key,{fontFamily:e.target.value})}>{RESULT_FONTS.map(font=><option key={font} value={font}>{font}</option>)}</select></label>
  <label>Dimensione <input type="number" aria-label={'Dimensione '+item.label} min="8" max="96" value={fmt.fontSize??(item.key==='sourceTitle'?22:16)} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=8&&n<=96)update(item.key,{fontSize:n})}}/></label>
  <label>Colore <input type="color" aria-label={'Colore '+item.label} value={fmt.color||(item.key.startsWith('question:')?'#2563eb':'#1f2937')} onChange={e=>update(item.key,{color:e.target.value})}/></label>
  {([['bold','Grassetto'],['italic','Corsivo'],['underline','Sottolineato'],['strikethrough','Barrato']] as const).map(([field,label])=><label key={field}><input type="checkbox" aria-label={label+' '+item.label} checked={fmt[field]??(field==='bold'&&(item.key.startsWith('option:')||item.key==='sourceTitle'))} onChange={e=>update(item.key,{[field]:e.target.checked})}/>{label}</label>)}
 </fieldset>})}</div>;
}
