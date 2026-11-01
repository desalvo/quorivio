import {useId} from 'react';
import type {WidgetTextStyle} from '../../api/src/domain';

/** Every shape/line is native SVG so it remains crisp in all slide views.
 * Graphics never intercept events used to select other widgets. */
export function WidgetGraphic({kind,style}:{kind:string;style?:WidgetTextStyle}){
 const gradientId=useId().replace(/:/g,'');
 if(kind!=='line'&&kind!=='shape')return null;
 const stroke=style?.strokeColor||'#334155';
 const width=Math.max(0,style?.strokeNone?0:(style?.strokeWidth??2));
 const dash=style?.strokeDash==='dash'?'6 4':style?.strokeDash==='dot'?'1 3':undefined;
 if(kind==='line'){
  const direction=style?.lineDirection||'horizontal';
  const coords:Record<string,[number,number,number,number]>={horizontal:[0,50,100,50],vertical:[50,0,50,100],diagonal:[0,0,100,100],reverse:[100,0,0,100]};
  const [x1,y1,x2,y2]=coords[direction]||coords.horizontal;
  return <svg className="widget-graphic-line" viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="Linea grafica"><line x1={x1} y1={y1} x2={x2} y2={y2} stroke={stroke} strokeWidth={width} strokeDasharray={dash} vectorEffect="non-scaling-stroke" strokeLinecap="round"/></svg>;
 }
 const shape=style?.shapeType||'rectangle';
 const paths:Record<string,string>={
  triangle:'M50 2 L98 98 L2 98 Z',diamond:'M50 2 L98 50 L50 98 L2 50 Z',
  hexagon:'M25 2 L75 2 L98 50 L75 98 L25 98 L2 50 Z',
  pentagon:'M50 2 L98 39 L79 98 L21 98 L2 39 Z',
  star:'M50 2 L61 36 L98 36 L68 58 L80 96 L50 72 L20 96 L32 58 L2 36 L39 36 Z',
  arrow:'M2 25 L62 25 L62 2 L98 50 L62 98 L62 75 L2 75 Z',
  heart:'M50 95 L5 55 Q-2 25 17 8 Q39 -2 50 22 Q61 -2 83 8 Q102 25 95 55 Z',
  cloud:'M6 44 L15 34 L27 32 L34 12 L47 8 L59 23 L72 17 L85 32 L95 42 L98 63 L85 81 L14 82 L2 65 Z',
  speech:'M2 2 L98 2 L98 78 L42 78 L25 98 L28 78 L2 78 Z'
 };
 const fill=style?.fillNone?'none':style?.fillMode==='gradient'?`url(#${gradientId})`:style?.fillColor||'#dbeafe';
 const common={fill,stroke:width>0?stroke:'none',strokeWidth:width,strokeDasharray:dash,vectorEffect:'non-scaling-stroke' as const,strokeLinejoin:'round' as const};
 return <svg className="widget-graphic-shape" viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label={'Forma '+shape}>
  <defs><linearGradient id={gradientId} x1="0" x2="1" y1="0" y2="1"><stop stopColor={style?.fillColor||'#dbeafe'}/><stop offset="100%" stopColor={style?.gradientEndColor||'#57a6f8'}/></linearGradient></defs>
  <g opacity={style?.fillOpacity??1}>
   {shape==='circle'||shape==='ellipse'?<ellipse cx="50" cy="50" rx={shape==='circle'?47:48} ry={shape==='circle'?47:47} {...common}/>:
    shape==='rounded-rectangle'?<rect x="2" y="2" width="96" height="96" rx="12" {...common}/>:
    <path d={paths[shape]||'M2 2 H98 V98 H2 Z'} {...common}/>}
  </g>
 </svg>;
}
