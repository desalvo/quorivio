/** The same default question hierarchy is used in authoring, rehearsal and live projection.
 * Only missing fields are filled: a saved custom style is never silently overwritten.
 */
import type {WidgetTextStyle} from '../../api/src/domain';
/** CSSStyleDeclaration accepts the literal family name "undefined". An absent
 * or malformed font must never become an authored face in ANY widget, schema,
 * imported layout, option, projection or rich-text span. Keep one allowlist
 * shared by all authoring renderers (the API validates the same choices). */
export const WIDGET_FONT_FAMILIES=['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'] as const;
export function safeWidgetFontFamily(value:unknown,fallback='Arial'):string{
 return typeof value==='string'&&WIDGET_FONT_FAMILIES.some(font=>font===value)?value:fallback;
}
export function explicitWidgetFontFamily(value:unknown):string|undefined{
 return typeof value==='string'&&WIDGET_FONT_FAMILIES.some(font=>font===value)?value:undefined;
}
export const QUESTION_TITLE_SIZE=22;
export const QUESTION_ANSWER_SIZE=16;
export function widgetTextDefaults(kind:string,style?:WidgetTextStyle):WidgetTextStyle|undefined {
 if(!['question','timed-quiz','topic-question'].includes(kind))return style;
 return {...style,
  fontFamily:safeWidgetFontFamily(style?.fontFamily),
  fontSize:style?.fontSize??QUESTION_TITLE_SIZE,
  bold:style?.bold??true,
  answerFontFamily:safeWidgetFontFamily(style?.answerFontFamily,safeWidgetFontFamily(style?.fontFamily)),
  answerFontSize:style?.answerFontSize??(style?.fontSize===undefined?QUESTION_ANSWER_SIZE:style.fontSize),
  answerBold:style?.answerBold??false};
}
export function initialWidgetTextStyle(kind:string):WidgetTextStyle {
 return widgetTextDefaults(kind,{fontFamily:'Arial'})||{fontFamily:'Arial'};
}
