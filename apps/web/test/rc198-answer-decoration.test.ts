import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {answerOptionStyle,answerInputStyle} from '../src/widget-answer-style.ts';
import {applyAllWidgetTypeface,styledSegments,type TextMark} from '../src/widget-text-marks.ts';
const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');

test('answer decoration remains independent from question title and is enabled or disabled explicitly',()=>{
 const style={underline:false,strikethrough:false,answerUnderline:true,answerStrikethrough:true};
 assert.equal(answerOptionStyle(style).textDecoration,'underline line-through');
 assert.equal(answerInputStyle(style).textDecoration,'underline line-through');
 assert.equal(answerOptionStyle({underline:true,strikethrough:true,answerUnderline:false,answerStrikethrough:false}).textDecoration,'none');
 assert.equal(answerOptionStyle().textDecoration,'none');
 assert.equal(answerOptionStyle({answerUnderline:true}).textDecoration,'underline');
 assert.equal(answerOptionStyle({answerStrikethrough:true}).textDecoration,'line-through');
});

test('whole-widget decoration overrides existing formatted answer and independent subquestion marks',()=>{
 const marks:TextMark[]=[
  {field:'option:a',start:0,end:4,style:{underline:false,strikethrough:false}},
  {field:'question:q1:option:a',start:0,end:4,style:{underline:false}},
  {field:'label',start:0,end:3,style:{underline:false}}
 ];
 const result=applyAllWidgetTypeface({style:{fontFamily:'Arial',answerUnderline:false},textMarks:marks},{underline:true,strikethrough:true});
 assert.equal(result.style.underline,true);
 assert.equal(result.style.strikethrough,true);
 assert.equal(result.style.answerUnderline,true);
 assert.equal(result.style.answerStrikethrough,true);
 assert.equal(answerOptionStyle(result.style).textDecoration,'underline line-through');
 for(const field of ['option:a','question:q1:option:a','label']){
  const actual=styledSegments(field==='label'?'ABC':'ABCD',result.textMarks,field);
  assert.ok(actual.every(piece=>piece.style.underline===true&&piece.style.strikethrough===true),field);
 }
 assert.equal(marks[0].style.underline,false); // no mutation of source
});

test('answer-only formatting targets independent answer properties and provides visible controls',()=>{
 assert.match(main,/underline:'answerUnderline',strikethrough:'answerStrikethrough'/);
 assert.match(main,/underline:questionStyle.answerUnderline\?\?questionStyle.underline/);
 // RC205 consolidated the formerly duplicated answer-only buttons into
 // the shared typography ribbon. Verify scope routing instead of old labels.
 assert.match(main,/effectiveScope==='answers'/);
 assert.match(main,/underline:'answerUnderline',strikethrough:'answerStrikethrough'/);
 assert.match(main,/fontFamily:'answerFontFamily'/);
 assert.match(main,/Risposta sottolineata/);
 assert.match(main,/Risposta barrata/);
});
