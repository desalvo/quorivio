/** Deterministic chart geometry for the editor, rehearsal and live presenter.
 * Percentages live OUTSIDE the pie with leaders, so even narrow segments remain legible.
 * Coordinates use a stable SVG viewBox; no DOM measurements or device-dependent pixels.
 */
export type PieSlice = {index:number;count:number;share:number;from:number;path:string;midAngle:number;label:string;side:'left'|'right';labelX:number;labelY:number;leader:string};
export const PIE_VIEWBOX = {width:500,height:320,cx:250,cy:160};
export const PIE_SIZE_DEFAULT = 72;
export function resultPieSize(value:unknown):number {
 return typeof value==='number'&&Number.isFinite(value)?Math.min(100,Math.max(40,value)):PIE_SIZE_DEFAULT;
}
export function resultPiePercent(share:number):string {
 const percentage=Math.max(0,share)*100;
 return `${percentage.toFixed(percentage<1?2:percentage<10?1:0)}%`;
}
const polar=(cx:number,cy:number,radius:number,angle:number)=>({x:cx+Math.cos(angle)*radius,y:cy+Math.sin(angle)*radius});
export function resultPieLayout(values:readonly number[],size:unknown=PIE_SIZE_DEFAULT,showPercentages=true,showNumbers=false):PieSlice[]{
 const clean=values.map(n=>Number.isFinite(n)&&n>0?n:0);
 const total=clean.reduce((a,b)=>a+b,0);
 if(total<=0)return [];
 const {cx,cy,height}=PIE_VIEWBOX;
 const radius=116*resultPieSize(size)/100;
 let previous=0;
 const slices:PieSlice[]=[];
 clean.forEach((count,index)=>{
  if(!count)return;
  const from=previous/total;
  previous+=count;
  const share=count/total;
  const a0=-Math.PI/2+2*Math.PI*from;
  const a1=-Math.PI/2+2*Math.PI*(from+share);
  const midAngle=(a0+a1)/2;
  const start=polar(cx,cy,radius,a0),end=polar(cx,cy,radius,a1);
  const path=share>=1-1e-12
   ?`M ${cx} ${cy-radius} A ${radius} ${radius} 0 1 1 ${cx} ${cy+radius} A ${radius} ${radius} 0 1 1 ${cx} ${cy-radius} Z`
   :`M ${cx} ${cy} L ${start.x} ${start.y} A ${radius} ${radius} 0 ${share>.5?1:0} 1 ${end.x} ${end.y} Z`;
  const side:PieSlice['side']=Math.cos(midAngle)<0?'left':'right';
  const label=[showNumbers?`${index+1}.`:'',showPercentages?resultPiePercent(share):''].filter(Boolean).join(' ');
  slices.push({index:index+1,count,share,from,path,midAngle,label,side,labelX:side==='left'?78:422,labelY:cy+Math.sin(midAngle)*(radius+19),leader:''});
 });
 // Compute labels on each side independently, keeping a minimum vertical gap.
 // Small slices clustered around the same angle receive separate leader lines.
 for(const side of ['left','right'] as const){
  const entries=slices.filter(s=>s.side===side).sort((a,b)=>a.labelY-b.labelY);
  if(!entries.length)continue;
  const top=19,bottom=height-19,spacing=Math.min(24,(bottom-top)/Math.max(1,entries.length-1));
  entries.forEach((s,i)=>{
   const minY=top+i*spacing;
   const maxY=bottom-(entries.length-1-i)*spacing;
   s.labelY=Math.min(maxY,Math.max(minY,s.labelY));
   if(i>0)s.labelY=Math.max(s.labelY,entries[i-1].labelY+spacing);
   const edge=polar(cx,cy,radius,s.midAngle);
   const elbow=polar(cx,cy,radius+12,s.midAngle);
   const lineEnd=side==='left'?86:414;
   s.leader=`${edge.x.toFixed(2)},${edge.y.toFixed(2)} ${elbow.x.toFixed(2)},${elbow.y.toFixed(2)} ${lineEnd},${s.labelY.toFixed(2)}`;
  });
 }
 return slices;
}
