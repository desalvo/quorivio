import type {WidgetAppearance} from './widget-appearance';
import {widgetShapeOutline} from './widget-appearance';

/** Same outline for the editor, rehearsal, presenter and audience; the SVG
 * preserves the authored polygon at any widget aspect ratio. */
export function WidgetShapeOutline({style}:{style:WidgetAppearance|undefined}){
 const edge=widgetShapeOutline(style);
 if(!edge)return null;
 const dash=edge.dash==='dash'?`${edge.width*4} ${edge.width*2.5}`:
  edge.dash==='dot'?`${edge.width} ${edge.width*2}`:undefined;
 return <svg className="widget-vector-outline" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true" focusable="false">
  <path d={edge.path} transform="translate(1.5 1.5) scale(.97)" fill="none" stroke={edge.color}
   strokeWidth={edge.width*4/3} strokeDasharray={dash} strokeLinecap={edge.dash==='dot'?'round':'butt'}
   strokeLinejoin="round" vectorEffect="non-scaling-stroke"/>
 </svg>;
}
