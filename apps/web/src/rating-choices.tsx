import React from 'react';

/** Identical 0–10 visual vocabulary in editor, rehearsal, public and presenter.
 * Read-only surfaces are explicitly disabled and never emit an answer. */
export function RatingChoices({view,size=16,readOnly=false,disabled=false,selected,onSelect}:{view?:string;size?:number;readOnly?:boolean;disabled?:boolean;selected?:string;onSelect?:(rating:number)=>void}){
 const inactive=readOnly||disabled||!onSelect;
 if(view==='select')return <select className="rating-choice-select" aria-label="Gradimento da zero a dieci" value={selected??''} disabled={inactive} onChange={event=>{if(event.target.value!=='')onSelect?.(Number(event.target.value))}}><option value="">Scegli un voto da 0 a 10</option>{Array.from({length:11},(_,rating)=><option key={rating} value={rating}>{rating}</option>)}</select>;
 return <div className="rating-choice-buttons" role="group" aria-label="Esprimi un voto da zero a dieci" style={{'--rating-font-size':`${Math.max(10,Math.min(64,size))/16}em`} as React.CSSProperties}>{Array.from({length:11},(_,rating)=><button type="button" key={rating} disabled={inactive} tabIndex={inactive?-1:undefined} aria-label={`Vota ${rating} su 10`} aria-pressed={selected===String(rating)} onClick={()=>onSelect?.(rating)}>{rating}</button>)}</div>;
}
