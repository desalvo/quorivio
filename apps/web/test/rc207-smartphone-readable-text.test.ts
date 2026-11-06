import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {answerOptionStyle,answerInputStyle,answerSubmitStyle} from '../src/widget-answer-style.ts';
import {inlineMarkCss} from '../src/widget-text-marks.ts';
import {mobileWidgetHeight,mobilePageWidgets} from '../src/mobile-page-layout.ts';
import {stageWidgetTypography} from '../src/stage-widget-typography.ts';

const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const rich=readFileSync(new URL('../src/widget-rich-editor.tsx',import.meta.url),'utf8');

test('RC207 smartphone uses real 390px font sizes, not 1280px cqw text',()=>{
 const answer=answerOptionStyle();
 assert.equal(answer['--q-phone-answer-font-size'],'18px');
 assert.equal(answer.fontSize,`${(16/12.8).toFixed(5)}cqw`,'desktop 1280px contract preserved');
 assert.equal(answerInputStyle()['--q-phone-answer-height'],'96px');
 const submit=answerSubmitStyle();
 assert.equal(submit['--q-phone-submit-font-size'],'18px');
 assert.equal(submit['--q-phone-submit-min-height'],'44px');
 assert.equal(submit.fontSize,`${(16/12.8).toFixed(5)}cqw`);
 assert.equal(stageWidgetTypography({id:'q',kind:'question',style:{fontFamily:'Arial'}},{},true).fontSize,'22px');
});

test('RC207 explicit author sizes and independent mobile overrides are retained',()=>{
 const style={fontFamily:'Georgia',fontSize:24,answerFontFamily:'Verdana',answerFontSize:26,answerFieldHeight:120,submitButtonSize:21};
 assert.equal(answerOptionStyle(style)['--q-phone-answer-font-size'],'26px');
 assert.equal(answerInputStyle(style)['--q-phone-answer-height'],'120px');
 assert.equal(answerSubmitStyle(style)['--q-phone-submit-font-size'],'21px');
 assert.equal(answerSubmitStyle(style)['--q-phone-submit-min-height'],'48px');
 const widgets=[{id:'q',kind:'question',style:{fontFamily:'Arial'},position:{x:0,y:0,width:70,height:20}}];
 const original=JSON.stringify(widgets);
 assert.equal(mobilePageWidgets(widgets,{styles:{q:{fontFamily:'Georgia',fontSize:30,answerFontSize:28}}})[0].style?.answerFontSize,28);
 assert.equal(JSON.stringify(widgets),original,'independent mobile style must not mutate desktop');
});

test('RC207 inline-marked text remains readable at its authored phone size',()=>{
 const marks=inlineMarkCss({fontSize:27,fontFamily:'Georgia'});
 assert.equal(marks.fontSize,`${(27/1280*100).toFixed(5)}cqw`);
 assert.equal(marks['--q-inline-phone-font-size'],'27px');
 assert.match(rich,/span\.style\.setProperty\('--q-inline-phone-font-size'/);
 assert.match(css,/\.widget-rich-inline span\[style\*="--q-inline-phone-font-size"\]/);
});

test('RC207 long answers reserve actual wrapped lines rather than shrinking controls',()=>{
 const short={id:'q',kind:'question',options:[{label:'Sì'},{label:'No'}]};
 const long={id:'q',kind:'question',options:[{label:'L'.repeat(255)},{label:'No'}]};
 assert.ok(mobileWidgetHeight(short)>=278);
 assert.ok(mobileWidgetHeight(long)>mobileWidgetHeight(short)+100);
 assert.equal(mobileWidgetHeight({id:'q',kind:'question',options:[]}),190);
 assert.match(css,/min-height:44px!important;align-items:center!important;padding:6px 0!important/);
 for(const surface of ['data-canvas-device="phone"','rehearsal-phone-stage','audience-widget-layout.stage-phone'])assert.ok(css.includes(surface));
});
