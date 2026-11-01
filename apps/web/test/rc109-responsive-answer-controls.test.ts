import test from 'node:test';
import assert from 'node:assert/strict';
import {answerInputStyle,answerSubmitStyle,requiresAnswerSubmit} from '../src/widget-answer-style.ts';
import {autoFitExpandedPosition,widgetMayAutoFit} from '../src/widget-auto-fit.ts';
import {newFooterWidget} from '../src/slide-master.ts';
import {validWidgetTextStyle,validPageDesign} from '../../api/src/domain.ts';

test('answer entry and submit styles are independent, bounded and accessible',()=>{
 const w={fontSize:30,answerFontFamily:'Georgia',answerFontSize:22,answerColor:'#225588',answerBold:true,answerItalic:true,submitButtonSize:25,answerFillColor:'#fef9ee'} as const;
 const input=answerInputStyle(w),submit=answerSubmitStyle(w);
 assert.equal(input.fontFamily,'Georgia');assert.equal(input.fontSize,'22px');assert.equal(input.color,'#225588');
 assert.equal(input.fontWeight,'700');assert.equal(input.fontStyle,'italic');assert.equal(input.backgroundColor,'#fef9ee');
 assert.equal(submit.fontSize,'25px');assert.ok(Number.parseInt(submit.minHeight)>=44);
 assert.equal(answerInputStyle({}).fontSize,'16px');
 assert.ok(requiresAnswerSubmit('question'));assert.ok(requiresAnswerSubmit('timed-quiz'));assert.ok(requiresAnswerSubmit('topic-question'));assert.ok(!requiresAnswerSubmit('title'));
});

test('server rejects unsafe response typography and button sizes',()=>{
 assert.ok(validWidgetTextStyle({answerFontFamily:'Georgia',answerFontSize:10,answerColor:'#aabbcc',answerBold:false,answerItalic:true,submitButtonSize:40}));
 for(const v of [-10,0,11,41,42,1.5,NaN,Infinity])assert.equal(validWidgetTextStyle({submitButtonSize:v}),false);
 for(const v of [9,97,14.3])assert.equal(validWidgetTextStyle({answerFontSize:v}),false);
 assert.equal(validWidgetTextStyle({answerFontFamily:'evil<script>'}),false);
 assert.equal(validWidgetTextStyle({answerColor:'red'}),false);
 assert.equal(validWidgetTextStyle({answerBold:'true'}),false);
 const widget={id:'w1',kind:'question',label:'Cosa pensi?',autoFit:true,style:{answerFontSize:19,submitButtonSize:18},position:{x:5,y:5,width:50,height:25,rotation:0}};
 assert.ok(validPageDesign({widgets:[widget]}));
 assert.equal(validPageDesign({widgets:[{...widget,autoFit:'yes'}]}),false);
});

test('autofit expands height without moving edges and stops at bottom of slide',()=>{
 const p={x:10,y:20,width:48,height:12,rotation:0};
 assert.deepEqual(autoFitExpandedPosition(p,35,500),{...p,height:20.6});
 assert.equal(autoFitExpandedPosition(p,0,500),null);
 assert.equal(autoFitExpandedPosition(p,5,0),null);
 assert.deepEqual(autoFitExpandedPosition({...p,y:90,height:5},2000,500),{...p,y:90,height:10});
 assert.ok(widgetMayAutoFit('question',undefined));assert.ok(widgetMayAutoFit('postit',true));
 assert.equal(widgetMayAutoFit('question',false),false);
 assert.equal(widgetMayAutoFit('footer'),false);
});

test('new footer is one slim row, centered and border-free as a shape',()=>{
 const w=newFooterWidget('footer-1');
 assert.equal(w.footerShowSessionTitle,true);
 assert.equal(w.footerShowPageNumber,true);
 assert.equal(w.position?.y,93);assert.equal(w.position?.height,7);
 assert.equal(w.style?.textAlign,'center');assert.equal(w.style?.strokeNone,true);
});
