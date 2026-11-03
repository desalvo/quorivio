import React from 'react';
import {REHEARSAL_EMOJIS} from './widget-results.js';
/** One visual/accessible component across editor, live presenter, rehearsal and audience. */
export function ReactionChoices({size=32,selected,readOnly=false,disabled=false,onSelect}:{size?:number;selected?:string;readOnly?:boolean;disabled?:boolean;onSelect?:(emoji:string)=>void}){
 const inactive=readOnly||disabled||!onSelect;
 return <div className="reaction-choice-buttons" role="group" aria-label="Reazioni disponibili" style={{'--reaction-size':`${Math.min(96,Math.max(16,size))/16}em`} as React.CSSProperties}>
  {REHEARSAL_EMOJIS.map(emoji=><button type="button" key={emoji} aria-label={'Reazione '+emoji} aria-pressed={selected===emoji} disabled={inactive} tabIndex={inactive?-1:undefined} onClick={()=>onSelect?.(emoji)}>{emoji}</button>)}
 </div>;
}
