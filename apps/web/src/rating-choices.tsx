import React from 'react';
import {RATING_VALUES} from './rating-range';
export {RATING_MIN,RATING_MAX,RATING_VALUES} from './rating-range';

/** Shared rating vocabulary on every surface. Exactly ten selectable values, 0–9. */
export function RatingChoices({view,size=16,readOnly=false,disabled=false,selected,onSelect}:{view?:string;size?:number;readOnly?:boolean;disabled?:boolean;selected?:string;onSelect?:(rating:number)=>void}){
 const inactive=readOnly||disabled||!onSelect;
 const current=selected!==undefined&&RATING_VALUES.includes(Number(selected))?selected:'';
 if(view==='select')return <select className="rating-choice-select" aria-label="Gradimento da zero a nove" value={current} disabled={inactive} onChange={event=>{if(event.target.value!=='')onSelect?.(Number(event.target.value))}}><option value="">Scegli un voto da 0 a 9</option>{RATING_VALUES.map(rating=><option key={rating} value={rating}>{rating}</option>)}</select>;
 return <div className="rating-choice-buttons" role="group" aria-label="Esprimi un voto da zero a nove" style={{'--rating-font-size':`${Math.max(10,Math.min(64,size))/16}em`} as React.CSSProperties}>{RATING_VALUES.map(rating=><button type="button" key={rating} disabled={inactive} tabIndex={inactive?-1:undefined} aria-label={`Vota ${rating} su 9`} aria-pressed={current===String(rating)} onClick={()=>onSelect?.(rating)}>{rating}</button>)}</div>;
}
