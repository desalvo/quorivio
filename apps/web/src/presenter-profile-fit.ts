/** Scale the whole presenter profile using the limiting frame dimension. */
export function presenterProfileScale(width:number,height:number):number{
 if(!Number.isFinite(width)||!Number.isFinite(height)||width<=0||height<=0)return 1;
 return Math.max(.05,Math.min(6,width/480,height/190));
}
