/** The same default question hierarchy is used in authoring, rehearsal and live projection.
 * Only missing fields are filled: a saved custom style is never silently overwritten.
 */
import type {WidgetTextStyle} from '../../api/src/domain';
export const QUESTION_TITLE_SIZE=22;
export const QUESTION_ANSWER_SIZE=16;
export function widgetTextDefaults(kind:string,style?:WidgetTextStyle):WidgetTextStyle|undefined {
 if(!['question','timed-quiz','topic-question'].includes(kind))return style;
 return {...style,
  fontFamily:style?.fontFamily||'Arial',
  fontSize:style?.fontSize??QUESTION_TITLE_SIZE,
  bold:style?.bold??true,
  answerFontFamily:style?.answerFontFamily||style?.fontFamily||'Arial',
  answerFontSize:style?.answerFontSize??(style?.fontSize===undefined?QUESTION_ANSWER_SIZE:style.fontSize),
  answerBold:style?.answerBold??false};
}
export function initialWidgetTextStyle(kind:string):WidgetTextStyle {
 return widgetTextDefaults(kind,{fontFamily:'Arial'})||{fontFamily:'Arial'};
}
