import assert from 'node:assert/strict';
import test from 'node:test';
import {validWidgetTextStyle,validPageDesign} from '../src/domain.ts';

test('free-answer background accepts a standalone six-digit color and remains valid in page layout',()=>{
 const w={id:'answer-box',kind:'question',label:'Domanda',answerMode:'text',position:{x:8,y:8,width:38,height:25},style:{fillColor:'#aabbcc',answerFillColor:'#112233'}};
 assert.equal(validWidgetTextStyle(w.style),true);
 assert.equal(validPageDesign({widgets:[w]}),true);
});
test('free-answer background fails closed for CSS injection and non-RGB inputs',()=>{
 for(const color of ['red','transparent','var(--token)','url(https://example.org)','rgba(0,0,0,0.4)','#fff','']){
  assert.equal(validWidgetTextStyle({answerFillColor:color}),false,color);
 }
});
