/** Input values may be temporarily empty while a person replaces an old size.
 * Never coerce an empty field to zero or discard a partially typed value. */
export function parsedEditableNumber(raw:string,min:number,max:number):number|null{
 if(!raw.trim())return null;
 const value=Number(raw.trim().replace(',','.'));
 return Number.isFinite(value)&&value>=min&&value<=max?value:null;
}
export function stepEditableNumber(raw:string,current:number,min:number,max:number,step:number,direction:-1|1):number{
 const n=parsedEditableNumber(raw,min,max)??current;
 const decimals=String(step).split('.')[1]?.length??0;
 return Math.min(max,Math.max(min,Number((n+direction*step).toFixed(Math.min(8,decimals+2)))));
}
