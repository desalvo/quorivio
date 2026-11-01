/** Response controls are independently styleable; never depend on the presenter title styles. */
import type {WidgetTextStyle} from '../../api/src/domain';
export const DEFAULT_SUBMIT_SIZE = 16;
export function answerInputStyle(style?:WidgetTextStyle){
 return {...answerOptionStyle(style),'--answer-color':style?.answerColor||'#152236',width:`${style?.answerFieldWidth??100}%`,height:`${style?.answerFieldHeight??96}px`,backgroundColor:style?.answerFillColor||(!style?.fillNone?style?.fillColor||'#ffffff':'#ffffff')};
}
export function answerOptionStyle(style?:WidgetTextStyle){
 return {fontFamily:style?.answerFontFamily||style?.fontFamily||'Arial',fontSize:`${style?.answerFontSize||style?.fontSize||16}px`,fontWeight:style?.answerBold?'700':'400',fontStyle:style?.answerItalic?'italic':'normal',color:style?.answerColor||'#152236'};
}
export function answerSubmitStyle(style?:WidgetTextStyle){
 const size=style?.submitButtonSize||DEFAULT_SUBMIT_SIZE;
 return {fontSize:`${size}px`,minHeight:`${Math.max(32,Math.ceil(size*2.25))}px`,padding:`${Math.max(5,Math.round(size*.35))}px ${Math.max(10,Math.round(size*.85))}px`};
}
export function requiresAnswerSubmit(kind:string){return kind==='question'||kind==='timed-quiz'||kind==='topic-question'}
