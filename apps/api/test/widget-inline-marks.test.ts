import test from 'node:test';
import assert from 'node:assert/strict';
import {validWidgetInlineMarks,validPageDesign} from '../src/domain.ts';
const widget=(textMarks:any[],label='Hello World')=>({widgets:[{id:'w1',kind:'text',label,textMarks,position:{x:5,y:5,width:30,height:20}}]});
test('plain-text labels retain bounded typography ranges through page schema',()=>{
 const good=[{field:'label',start:0,end:5,style:{fontFamily:'Georgia',fontSize:22,color:'#123456',bold:true}}];
 assert.equal(validPageDesign(widget(good)),true);
});
test('range cannot extend beyond actual label or refer to absent option',()=>{
 assert.equal(validPageDesign(widget([{field:'label',start:3,end:20,style:{bold:true}}])),false);
 assert.equal(validPageDesign(widget([{field:'option:o1',start:0,end:1,style:{italic:true}}])),false);
});
test('options retain their own independent ranges',()=>{
 assert.equal(validPageDesign({widgets:[{id:'q',kind:'question',label:'Q',answerMode:'single',options:[{id:'opt_1',label:'Answer'}],textMarks:[{field:'option:opt_1',start:0,end:6,style:{color:'#abc123'}}]}]}),true);
});
test('reject injected HTML, unknown CSS, unbounded fonts and malformed offsets',()=>{
 const invalid=[
  [{field:'label',start:0,end:2,style:{position:'fixed'}}],
  [{field:'label',start:0,end:2,style:{color:'url(javascript:alert(1))'}}],
  [{field:'label',start:0,end:2,style:{fontSize:1000}}],
  [{field:'label',start:-1,end:2,style:{bold:true}}],
  [{field:'label',start:2,end:2,style:{bold:true}}],
  [{field:'onload',start:0,end:2,style:{bold:true}}],
  [{field:'label',start:0,end:2,style:{bold:true},extra:'<svg>'}],
  Array.from({length:65},()=>({field:'label',start:0,end:2,style:{bold:true}}))
 ];
 for(const marks of invalid)assert.equal(validWidgetInlineMarks(marks),false,JSON.stringify(marks).slice(0,65));
});
