import React from 'react';
import {areaPath,chartOpacity,chartStrokeWidth,chartTotal,cleanChartRows,donutSlices,
 lineChartPoints,linePath,LINE_PLOT,radarAreaPath,radarAxisTip,radarPoints,radarRing,
 RADAR,validAdvancedChartKind,type AdvancedChartOptions,type AdvancedChartRow,
 type AdvancedChartKind} from './result-advanced-chart-geometry.js';

const PALETTE=['#277fd1','#e87947','#51a580','#a477ca','#d35482','#b5a337'];
const safeColor=(value:unknown,index:number)=>typeof value==='string'&&/^#[0-9a-f]{6}$/i.test(value)?value:PALETTE[index%PALETTE.length];
const short=(value:string,max=11)=>value.length>max?value.slice(0,max-1)+'…':value;
/** Accessible chart shared by editor, rehearsal, projection and live result panels.
 * Every SVG mark has aggregate count/percentage metadata; no participant PII. */
export function ResultAdvancedChart({kind,rows,colors=[],config={}}:{
 kind:AdvancedChartKind;rows:readonly AdvancedChartRow[];colors?:readonly string[];config?:AdvancedChartOptions;
}){
 if(!validAdvancedChartKind(kind))return null;
 const data=cleanChartRows(rows),total=chartTotal(data),hasAnswers=total>0;
 const color=(i:number)=>safeColor(colors[i],i);
 const line=kind==='line'||kind==='area',points=line?lineChartPoints(data):[];
 const path=line?linePath(points,config.chartSmooth===true):'';
 const radar=kind==='radar'?radarPoints(data):[];
 const donut=kind==='donut'?donutSlices(data,config.donutHoleSize):[];
 const showPoints=config.chartShowPoints!==false,showValues=config.chartShowValues!==false;
 const width=chartStrokeWidth(config.chartStrokeWidth),opacity=chartOpacity(config.chartFillOpacity);
 const description=data.map(r=>`${r.label}: ${r.count}`).join('; ');
 const names:{[K in AdvancedChartKind]:string}={line:'Linee',area:'Area',donut:'Donut',radar:'Radar'};
 const max=Math.max(1,...data.map(r=>r.count));
 const heading=`Grafico ${names[kind]}: ${total} risposte`;
 const cx=280,cy=144;
 return <svg className={`linked-results-advanced-chart linked-results-chart-${kind}`} role="img"
  viewBox="0 0 560 300" preserveAspectRatio="xMidYMid meet" data-chart-type={kind}
  data-chart-total={total} aria-label={heading}>
  <title>{heading}</title><desc>{description||'Nessuna risposta registrata'}</desc>
  {line&&<>
   {[0,.25,.5,.75,1].map(f=>{
    const y=LINE_PLOT.bottom-(LINE_PLOT.bottom-LINE_PLOT.top)*f;
    return <g key={'grid-'+f} aria-hidden="true"><line x1={LINE_PLOT.left} y1={y} x2={LINE_PLOT.right} y2={y} stroke="#dce4f0" strokeWidth="1"/><text x={LINE_PLOT.left-10} y={y+5} textAnchor="end" fontSize="12" fill="#4c6075">{Math.round(max*f)}</text></g>;
   })}
   {data.map((r,i)=><text key={'xtick-'+r.id+'-'+i} x={points[i].x} y="276" textAnchor="middle" fontSize={data.length>8?10:12} fill="#394e65"><title>{r.label}</title>{short(r.label,data.length>8?7:11)}</text>)}
   {kind==='area'&&hasAnswers&&<path d={areaPath(points,config.chartSmooth===true)} fill={color(0)} fillOpacity={opacity} stroke="none"/>}
   {hasAnswers&&<path d={path} fill="none" stroke={color(0)} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round"/>}
   {points.map((point,i)=><g key={'dot-'+point.id+'-'+i}>
    {showPoints&&<circle cx={point.x} cy={point.y} r={Math.max(3,width+2)} fill={color(i)} stroke="#ffffff" strokeWidth="2"><title>{point.label}: {point.count} risposte</title></circle>}
    {showValues&&<text x={point.x} y={Math.max(15,point.y-11)} textAnchor="middle" fontSize="12" fontWeight="700" fill="#18274e">{point.count}</text>}
   </g>)}
  </>}
  {kind==='donut'&&<>
   {donut.length===0&&<circle cx={cx} cy={cy} r="108" fill="none" stroke="#dce4f0" strokeWidth={108*(1-(Math.max(20,Math.min(80,config.donutHoleSize??55))/100))}/>}
   {donut.map((slice,i)=>{
    const index=data.findIndex(r=>r.id===slice.id);
    return <g key={'donut-'+slice.id+'-'+i}>
     <path d={slice.path} fill={color(Math.max(0,index))} stroke="#ffffff" strokeWidth="1.8" fillRule="evenodd">
      <title>{slice.label}: {slice.count} risposte ({slice.percent.toFixed(1)}%)</title>
     </path>
     {config.chartShowPercentages===true&&slice.percent>=10&&<text x={slice.midX} y={slice.midY+4} fontSize="12" fontWeight="700" textAnchor="middle" fill="#ffffff" stroke="#16203d" strokeWidth=".4" paintOrder="stroke">{Math.round(slice.percent)}%</text>}
    </g>;
   })}
   <text x={cx} y={cy+1} textAnchor="middle" fontWeight="800" fontSize="30" fill="#172650">{total}</text>
   <text x={cx} y={cy+23} textAnchor="middle" fontSize="12" fill="#4c6075">risposte</text>
  </>}
  {kind==='radar'&&<>
   {data.length<3?<text x="280" y="150" fill="#405b72" fontSize="16" textAnchor="middle">Radar: servono almeno 3 opzioni</text>:<>
    {Array.from({length:Math.max(2,Math.min(8,config.radarGridLevels??4))},(_,i)=>{
     const levels=Math.max(2,Math.min(8,config.radarGridLevels??4));
     return <path key={'radar-grid-'+i} d={radarRing(data.length,(i+1)/levels)} fill="none" stroke="#dce4f0" strokeWidth="1.5"/>;
    })}
    {data.map((r,i)=>{
     const tip=radarAxisTip(i,data.length);
     return <g key={'radar-axis-'+r.id+'-'+i}>
      <line x1={RADAR.cx} y1={RADAR.cy} x2={tip.x} y2={tip.y} stroke="#dce4f0"/>
      <text x={tip.x} y={tip.y+4} fontSize={data.length>8?10:12} textAnchor="middle" fill="#344b61"><title>{r.label}</title>{short(r.label,data.length>8?7:11)}</text>
     </g>;
    })}
    {hasAnswers&&<path d={radarAreaPath(radar)} fill={color(0)} fillOpacity={opacity} stroke={color(0)} strokeWidth={width} strokeLinejoin="round"/>}
    {radar.map((point,i)=><g key={'radar-dot-'+point.id+'-'+i}>
     {showPoints&&<circle cx={point.x} cy={point.y} r={Math.max(3,width+1)} fill={color(i)} stroke="white" strokeWidth="2"><title>{point.label}: {point.count} risposte</title></circle>}
     {showValues&&<text x={point.x} y={point.y-10} fill="#172650" textAnchor="middle" fontSize="11" fontWeight="700">{point.count}</text>}
    </g>)}
   </>}
  </>}
 </svg>;
}
