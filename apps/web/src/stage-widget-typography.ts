/** Stage typography shared by the live participant and rehearsal stage.
 * The phone presentation uses an actual 390px document, not a 1280px canvas
 * scaled down: use logical pixels there, but resolve the schema's master title
 * font before applying mobile overrides. Both surfaces must match exactly.
 */
import type {WidgetTextStyle} from '../../api/src/domain';
import {widgetDisplay,type SlideWidget} from './slide-master.ts';
import {widgetTypographyStyle} from './widget-appearance.ts';

export function stageWidgetTypography(
 widget:SlideWidget,
 context:{pageTitle?:string;masterTitleStyle?:WidgetTextStyle},
 phone=false
):Record<string,string|undefined>{
 const resolved=widget.kind==='title'?widgetDisplay(widget,context).style:widget.style;
 const typography=widgetTypographyStyle(resolved);
 const base={...typography,'--authored-widget-font-size':typography.fontSize};
 if(!phone)return base;
 const px=`${resolved?.fontSize??16}px`;
 return {...base,fontSize:px,'--mobile-widget-font-size':px};
}
