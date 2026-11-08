/** Response controls are independently styleable; never depend on the presenter title styles. */
import type {WidgetTextStyle} from '../../api/src/domain';
import {safeWidgetFontFamily} from './widget-typography-defaults.ts';
export const DEFAULT_SUBMIT_SIZE = 16;
export function answerInputStyle(style?:WidgetTextStyle){
 return {...answerOptionStyle(style),'--answer-color':style?.answerColor||'#152236',width:`${style?.answerFieldWidth??100}%`,height:`${((style?.answerFieldHeight??96)/12.8).toFixed(5)}cqw`,'--q-phone-answer-height':`${style?.answerFieldHeight??96}px`,backgroundColor:style?.answerFillColor||(!style?.fillNone?style?.fillColor||'#ffffff':'#ffffff')};
}
export function answerOptionStyle(style?:WidgetTextStyle){
 const family=safeWidgetFontFamily(style?.answerFontFamily,safeWidgetFontFamily(style?.fontFamily));
 const size=`${((style?.answerFontSize||style?.fontSize||16)/12.8).toFixed(5)}cqw`;
 return {fontFamily:family,fontSize:size,'--q-answer-font-family':family,'--q-answer-font-size':size,
  // 390px smartphone stages must not use desktop/1280 cqw for answer text.
  '--q-phone-answer-font-size':`${style?.answerFontSize??style?.fontSize??18}px`,
  fontWeight:style?.answerBold?'700':'400',fontStyle:style?.answerItalic?'italic':'normal',
  textDecoration:[style?.answerUnderline?'underline':'',style?.answerStrikethrough?'line-through':''].filter(Boolean).join(' ')||'none',
  color:style?.answerColor||'#152236'};
}
export function answerSubmitStyle(style?:WidgetTextStyle){
 const size=style?.submitButtonSize||DEFAULT_SUBMIT_SIZE;
 return {fontFamily:safeWidgetFontFamily(style?.submitFontFamily,safeWidgetFontFamily(style?.fontFamily)),
  '--q-phone-submit-font-size':`${style?.submitButtonSize??18}px`,
  '--q-phone-submit-min-height':`${Math.max(44,Math.ceil((style?.submitButtonSize??18)*2.25))}px`,
  '--q-phone-submit-padding':`${Math.max(7,Math.round((style?.submitButtonSize??18)*.35))}px ${Math.max(12,Math.round((style?.submitButtonSize??18)*.85))}px`,
  fontWeight:style?.submitBold===false?'400':'700',fontStyle:style?.submitItalic?'italic':'normal',textDecoration:[style?.submitUnderline?'underline':'',style?.submitStrikethrough?'line-through':''].filter(Boolean).join(' ')||'none',color:style?.submitColor||'#142c43','--q-submit-color':style?.submitColor||'#142c43',fontSize:`${(size/12.8).toFixed(5)}cqw`,minHeight:`${(Math.max(32,Math.ceil(size*2.25))/12.8).toFixed(5)}cqw`,padding:`${(Math.max(5,Math.round(size*.35))/12.8).toFixed(5)}cqw ${(Math.max(10,Math.round(size*.85))/12.8).toFixed(5)}cqw`};
}
export function requiresAnswerSubmit(kind:string){return kind==='question'||kind==='timed-quiz'||kind==='topic-question'}
