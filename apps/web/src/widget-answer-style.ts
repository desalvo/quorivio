/** Response controls are independently styleable; never depend on the presenter title styles. */
import type {WidgetTextStyle} from '../../api/src/domain';
export const DEFAULT_SUBMIT_SIZE = 16;
export function answerInputStyle(style?:WidgetTextStyle){
 return {...answerOptionStyle(style),'--answer-color':style?.answerColor||'#152236',width:`${style?.answerFieldWidth??100}%`,height:`${((style?.answerFieldHeight??96)/12.8).toFixed(5)}cqw`,backgroundColor:style?.answerFillColor||(!style?.fillNone?style?.fillColor||'#ffffff':'#ffffff')};
}
export function answerOptionStyle(style?:WidgetTextStyle){
 const family=style?.answerFontFamily||style?.fontFamily||'Arial';
 const size=`${((style?.answerFontSize||style?.fontSize||16)/12.8).toFixed(5)}cqw`;
 return {fontFamily:family,fontSize:size,'--q-answer-font-family':family,'--q-answer-font-size':size,
  fontWeight:style?.answerBold?'700':'400',fontStyle:style?.answerItalic?'italic':'normal',color:style?.answerColor||'#152236'};
}
export function answerSubmitStyle(style?:WidgetTextStyle){
 const size=style?.submitButtonSize||DEFAULT_SUBMIT_SIZE;
 return {fontSize:`${(size/12.8).toFixed(5)}cqw`,minHeight:`${(Math.max(32,Math.ceil(size*2.25))/12.8).toFixed(5)}cqw`,padding:`${(Math.max(5,Math.round(size*.35))/12.8).toFixed(5)}cqw ${(Math.max(10,Math.round(size*.85))/12.8).toFixed(5)}cqw`};
}
export function requiresAnswerSubmit(kind:string){return kind==='question'||kind==='timed-quiz'||kind==='topic-question'}
