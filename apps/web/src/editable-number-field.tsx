import React,{useEffect,useRef,useState} from 'react';
import {parsedEditableNumber,stepEditableNumber} from './editable-number-value.js';

/** Shared number input in Format Widget: editable by typing, keyboard arrows,
 * and explicit buttons (even when a browser suppresses native spin controls).
 * Prop changes never erase a user's in-progress edit. */
export function EditableNumberField({value,min,max,step=1,ariaLabel,onCommit,className='',disabled=false,autoApply=false}:{value:number;min:number;max:number;step?:number;ariaLabel:string;onCommit:(next:number)=>void;className?:string;disabled?:boolean;autoApply?:boolean}){
 const [draft,setDraft]=useState(String(value));
 const focused=useRef(false);
 const valueRef=useRef(value);
 valueRef.current=value;
 useEffect(()=>{if(!focused.current)setDraft(String(value))},[value]);
 const commit=(raw:string)=>{
  const next=parsedEditableNumber(raw,min,max);
  if(next===null){setDraft(String(valueRef.current));return}
  setDraft(String(next));
  if(next!==valueRef.current)onCommit(next);
 };
 const stepBy=(direction:-1|1)=>{
  const next=stepEditableNumber(draft,valueRef.current,min,max,step,direction);
  setDraft(String(next));
  if(next!==valueRef.current)onCommit(next);
 };
 return <span className={'editable-number-field '+className} role="group" aria-label={ariaLabel}>
  <input type="number" min={min} max={max} step={step} inputMode={Number.isInteger(step)?'numeric':'decimal'} aria-label={ariaLabel} disabled={disabled} value={draft}
   onFocus={e=>{focused.current=true;e.currentTarget.select()}}
   onChange={e=>{const next=e.currentTarget.value;setDraft(next);if(autoApply){const n=parsedEditableNumber(next,min,max);if(n!==null&&n!==valueRef.current)onCommit(n)}}}
   onBlur={e=>{focused.current=false;commit(e.currentTarget.value)}}
   onKeyDown={e=>{e.stopPropagation();if(e.key==='Enter'){e.preventDefault();e.currentTarget.blur()}else if(e.key==='Escape'){e.preventDefault();setDraft(String(valueRef.current));e.currentTarget.blur()}else if(e.key==='ArrowUp'||e.key==='ArrowDown'){e.preventDefault();stepBy(e.key==='ArrowUp'?1:-1)}}}/>
  <span className="editable-number-arrows">
   <button type="button" aria-label={'Aumenta '+ariaLabel+' di '+step} title={'Aumenta di '+step} disabled={disabled} onMouseDown={e=>e.preventDefault()} onClick={()=>stepBy(1)}>▲</button>
   <button type="button" aria-label={'Diminuisci '+ariaLabel+' di '+step} title={'Diminuisci di '+step} disabled={disabled} onMouseDown={e=>e.preventDefault()} onClick={()=>stepBy(-1)}>▼</button>
  </span>
 </span>;
}
