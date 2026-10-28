/** Consistent, server-validated appearance for editor, rehearsal and live view. */
import type {WidgetTextStyle} from '../../api/src/domain';
/** Exact subset of the server-validated style contract, not an independent schema. */
export type WidgetAppearance = Pick<WidgetTextStyle,
 'fillColor'|'fillNone'|'fillMode'|'fillOpacity'|'gradientEndColor'|'fillImageAssetId'|
 'ratingView'|'strokeColor'|'strokeNone'|'strokeWidth'|'strokeDash'|'rounded'|'shapeType'>;

const rgbaHex=(hex:string,alpha:number)=>/^#[a-f\d]{6}$/i.test(hex)?hex+Math.round(Math.max(0,Math.min(1,alpha))*255).toString(16).padStart(2,'0'):undefined;
const polygon:Record<string,string>={
 triangle:'polygon(50% 0%,100% 100%,0% 100%)',
 diamond:'polygon(50% 0%,100% 50%,50% 100%,0% 50%)',
 hexagon:'polygon(25% 0%,75% 0%,100% 50%,75% 100%,25% 100%,0% 50%)',
 speech:'polygon(0 0,100% 0,100% 78%,42% 78%,25% 100%,28% 78%,0 78%)',
 cloud:'polygon(6% 43%,15% 34%,27% 32%,34% 12%,47% 8%,59% 23%,72% 17%,85% 32%,95% 42%,98% 63%,85% 81%,14% 82%,2% 65%)'
};
export function widgetAppearanceStyle(style:WidgetAppearance|undefined,imageUrl?:string):Record<string,string|number|undefined>{
 if(!style)return {};
 const borderEnabled=!style.strokeNone&&(!!style.strokeColor||style.strokeWidth!==undefined||style.strokeDash!==undefined);
 const dash=style.strokeDash==='dash'?'dashed':style.strokeDash==='dot'?'dotted':'solid';
 const alpha=style.fillOpacity??1;
 const color=rgbaHex(style.fillColor||'#ffffff',alpha);
 const end=rgbaHex(style.gradientEndColor||'#57a6f8',alpha);
 const image=style.fillMode==='image'&&!style.fillNone&&style.fillImageAssetId&&imageUrl?`url("${imageUrl}")`:undefined;
 const gradient=style.fillMode==='gradient'&&!style.fillNone?`linear-gradient(135deg, ${color}, ${end})`:undefined;
 const shape=style.shapeType||'';
 const result:Record<string,string|number|undefined>={
  backgroundColor:style.fillNone?'transparent':!image&&!gradient?(alpha===1?style.fillColor||undefined:color):undefined,
  borderStyle:style.strokeNone?'none':borderEnabled?dash:undefined,
  borderColor:style.strokeNone?'transparent':borderEnabled?(style.strokeColor||'#334155'):undefined,
  borderWidth:style.strokeNone?0:borderEnabled?`${style.strokeWidth??1}pt`:undefined,
  borderRadius:shape==='circle'||shape==='ellipse'?'50%':shape==='rounded-rectangle'||style.rounded?14:undefined,
  clipPath:polygon[shape]
 };
 if(image||gradient){result.backgroundImage=image||gradient;}
 if(image){result.backgroundPosition='center';result.backgroundSize='cover';}
 if(shape==='circle')result.aspectRatio='1';
 return result;
}

/** Font and paragraph values belong to the stage coordinate system (1280px wide),
 * not to each viewport. Using cqw ensures identical scaling in editor, preview
 * and presenter projection without per-surface magic font sizes. */
export function widgetTypographyStyle(style:WidgetTextStyle|undefined):Record<string,string|undefined>{
 const size=style?.fontSize??16;
 return {
  fontFamily:style?.fontFamily||undefined,
  fontSize:`${(size/1280*100).toFixed(5)}cqw`,
  color:style?.color||undefined,
  fontWeight:style?.bold?'bold':undefined,
  fontStyle:style?.italic?'italic':undefined,
  textAlign:style?.textAlign||undefined,
  textDecoration:[style?.underline?'underline':'',style?.strikethrough?'line-through':''].filter(Boolean).join(' ')||undefined
 };
}
