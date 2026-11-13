/** Deterministic, safe SVG geometry for Quorivio linked/live result charts.
 * Counts are aggregated votes, never participant identities. The renderer uses
 * the same stable geometry across editor, rehearsal, projection and phone.
 */
export type AdvancedChartKind='line'|'area'|'donut'|'radar';
export type AdvancedChartRow={id:string;label:string;count:number};
export type AdvancedChartOptions={
 chartSmooth?:boolean;chartShowPoints?:boolean;chartShowValues?:boolean;
 chartShowPercentages?:boolean;chartStrokeWidth?:number;chartFillOpacity?:number;
 donutHoleSize?:number;radarGridLevels?:number;
};
export type ChartPoint={id:string;label:string;count:number;x:number;y:number;percent:number};
export type DonutSlice={id:string;label:string;count:number;percent:number;path:string;midX:number;midY:number};
export const CHART_WIDTH=560,CHART_HEIGHT=300;
export const CHART_TYPES:readonly AdvancedChartKind[]=['line','area','donut','radar'] as const;
export function validAdvancedChartKind(value:unknown):value is AdvancedChartKind{
 return typeof value==='string'&&(CHART_TYPES as readonly string[]).includes(value);
}
export function finiteChartNumber(value:unknown,min:number,max:number,fallback:number):number{
 return typeof value==='number'&&Number.isFinite(value)?Math.max(min,Math.min(max,value)):fallback;
}
export function chartOpacity(value:unknown):number{return finiteChartNumber(value,0,100,35)/100;}
export function chartStrokeWidth(value:unknown):number{return finiteChartNumber(value,1,8,3);}
export function cleanChartRows(rows:readonly AdvancedChartRow[]):AdvancedChartRow[]{
 return rows.slice(0,20).map((r,i)=>({id:String(r.id??i),label:String(r.label??''),count:typeof r.count==='number'&&Number.isFinite(r.count)&&r.count>0?Math.floor(r.count):0}));
}
export function chartTotal(rows:readonly AdvancedChartRow[]):number{return cleanChartRows(rows).reduce((a,r)=>a+r.count,0);}
export const LINE_PLOT={left:56,right:526,top:40,bottom:249} as const;
export function lineChartPoints(rows:readonly AdvancedChartRow[]):ChartPoint[]{
 const clean=cleanChartRows(rows),{left,right,top,bottom}=LINE_PLOT,total=chartTotal(clean);
 const max=Math.max(1,...clean.map(r=>r.count));
 return clean.map((r,index)=>({id:r.id,label:r.label,count:r.count,
  x:clean.length===1?(left+right)/2:left+(right-left)*index/(clean.length-1),
  y:bottom-(bottom-top)*r.count/max,percent:total>0?r.count/total*100:0}));
}
export function linePath(points:readonly Pick<ChartPoint,'x'|'y'>[],smooth=false):string{
 if(!points.length)return '';
 let result=`M ${points[0].x.toFixed(2)} ${points[0].y.toFixed(2)}`;
 for(let i=1;i<points.length;i++){
  const a=points[i-1],b=points[i];
  if(smooth){const mid=(a.x+b.x)/2;result+=` C ${mid.toFixed(2)} ${a.y.toFixed(2)} ${mid.toFixed(2)} ${b.y.toFixed(2)} ${b.x.toFixed(2)} ${b.y.toFixed(2)}`;}
  else result+=` L ${b.x.toFixed(2)} ${b.y.toFixed(2)}`;
 }
 return result;
}
export function areaPath(points:readonly ChartPoint[],smooth=false):string{
 if(!points.length)return '';
 return `${linePath(points,smooth)} L ${points[points.length-1].x.toFixed(2)} ${LINE_PLOT.bottom} L ${points[0].x.toFixed(2)} ${LINE_PLOT.bottom} Z`;
}
const polar=(cx:number,cy:number,r:number,a:number)=>({x:cx+r*Math.cos(a),y:cy+r*Math.sin(a)});
const fmt=(n:number)=>n.toFixed(3);
/** Donut segments use opposite-winding inner arcs. 100% slices require two arcs. */
export function donutSlicePath(cx:number,cy:number,outer:number,inner:number,start:number,end:number):string{
 const sweep=end-start;if(!(sweep>0)||inner>=outer||inner<0)return '';
 const p0=polar(cx,cy,outer,start),p1=polar(cx,cy,outer,end),q0=polar(cx,cy,inner,start),q1=polar(cx,cy,inner,end);
 if(sweep>=Math.PI*2-1e-10){
  const pm=polar(cx,cy,outer,start+Math.PI),qm=polar(cx,cy,inner,start+Math.PI);
  return `M ${fmt(p0.x)} ${fmt(p0.y)} A ${outer} ${outer} 0 1 1 ${fmt(pm.x)} ${fmt(pm.y)} A ${outer} ${outer} 0 1 1 ${fmt(p0.x)} ${fmt(p0.y)} L ${fmt(q0.x)} ${fmt(q0.y)} A ${inner} ${inner} 0 1 0 ${fmt(qm.x)} ${fmt(qm.y)} A ${inner} ${inner} 0 1 0 ${fmt(q0.x)} ${fmt(q0.y)} Z`;
 }
 return `M ${fmt(p0.x)} ${fmt(p0.y)} A ${outer} ${outer} 0 ${sweep>Math.PI?1:0} 1 ${fmt(p1.x)} ${fmt(p1.y)} L ${fmt(q1.x)} ${fmt(q1.y)} A ${inner} ${inner} 0 ${sweep>Math.PI?1:0} 0 ${fmt(q0.x)} ${fmt(q0.y)} Z`;
}
export function donutSlices(rows:readonly AdvancedChartRow[],holeSize:unknown=55):DonutSlice[]{
 const clean=cleanChartRows(rows),total=chartTotal(clean);if(total<=0)return [];
 const r=108,inner=r*finiteChartNumber(holeSize,20,80,55)/100,cx=280,cy=144;
 let offset=0;
 return clean.flatMap(item=>{
  if(item.count<=0)return [];
  const start=-Math.PI/2+Math.PI*2*offset/total;offset+=item.count;
  const end=-Math.PI/2+Math.PI*2*offset/total,mid=(start+end)/2;
  const p=polar(cx,cy,(r+inner)/2,mid);
  return [{id:item.id,label:item.label,count:item.count,percent:item.count/total*100,path:donutSlicePath(cx,cy,r,inner,start,end),midX:p.x,midY:p.y}];
 });
}
export const RADAR={cx:280,cy:151,radius:103} as const;
export function radarPoints(rows:readonly AdvancedChartRow[]):ChartPoint[]{
 const clean=cleanChartRows(rows),total=chartTotal(clean),max=Math.max(1,...clean.map(r=>r.count));
 return clean.map((r,i)=>{
  const angle=-Math.PI/2+Math.PI*2*i/clean.length;
  const p=polar(RADAR.cx,RADAR.cy,RADAR.radius*r.count/max,angle);
  return {id:r.id,label:r.label,count:r.count,x:p.x,y:p.y,percent:total>0?r.count/total*100:0};
 });
}
export function radarRing(count:number,fraction:number):string{
 if(count<3||!Number.isInteger(count))return '';
 return Array.from({length:count},(_,i)=>{
  const angle=-Math.PI/2+Math.PI*2*i/count,p=polar(RADAR.cx,RADAR.cy,RADAR.radius*fraction,angle);
  return `${i?'L':'M'} ${fmt(p.x)} ${fmt(p.y)}`;
 }).join(' ')+' Z';
}
export function radarAreaPath(points:readonly ChartPoint[]):string{
 return points.length<3?'':points.map((p,i)=>`${i?'L':'M'} ${fmt(p.x)} ${fmt(p.y)}`).join(' ')+' Z';
}
export function radarAxisTip(index:number,count:number,margin=19){
 const angle=-Math.PI/2+2*Math.PI*index/count;
 return polar(RADAR.cx,RADAR.cy,RADAR.radius+margin,angle);
}
