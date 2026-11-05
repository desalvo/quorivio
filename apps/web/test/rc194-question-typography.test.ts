import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {widgetTextDefaults,initialWidgetTextStyle} from '../src/widget-typography-defaults.ts';
import {applyAllWidgetTypeface,remapMarks,styledSegments,styleOfPreviousCharacter,type TextMark} from '../src/widget-text-marks.ts';

const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('every new question and quiz starts with Arial bold 22pt-like title and Arial regular 16px answer',()=>{
 for(const kind of ['question','timed-quiz','topic-question']){
  const value=initialWidgetTextStyle(kind);
  assert.equal(value.fontFamily,'Arial'); assert.equal(value.bold,true);
  assert.equal(value.fontSize,22);assert.equal(value.answerFontSize,16);
  assert.equal(value.answerFontFamily,'Arial');assert.equal(value.answerBold,false);
 }
});
test('older question/quiz layouts resolve defaults without mutating persisted custom styles',()=>{
 const authored={fontFamily:'Georgia',fontSize:26,bold:false,answerFontFamily:'Tahoma',answerFontSize:19,answerBold:true};
 assert.deepEqual(widgetTextDefaults('question',authored),authored);
 assert.equal(widgetTextDefaults('question',{})?.fontSize,22);
 assert.equal(widgetTextDefaults('timed-quiz',{})?.answerFontSize,16);
 assert.equal(widgetTextDefaults('text',undefined),undefined);
 const customSize=widgetTextDefaults('question',{fontSize:30});
 assert.equal(customSize?.answerFontSize,30); // explicit older size remains consistent
});
test('whole widget font changes propagate to every answer and independent question text mark',()=>{
 const marks:TextMark[]=[
  {field:'label',start:0,end:4,style:{fontFamily:'Verdana'}},
  {field:'description',start:0,end:4,style:{fontFamily:'Tahoma'}},
  {field:'option:o1',start:0,end:4,style:{fontFamily:'Arial'}},
  {field:'question:q1:label',start:0,end:4,style:{fontFamily:'Verdana'}},
  {field:'question:q1:option:o1',start:0,end:4,style:{fontFamily:'Tahoma'}}
 ];
 const result=applyAllWidgetTypeface({style:{fontFamily:'Arial',answerFontFamily:'Arial'},textMarks:marks},{fontFamily:'Georgia'});
 assert.equal(result.style.fontFamily,'Georgia');
 assert.equal(result.style.answerFontFamily,'Georgia');
 assert.ok(result.textMarks.every(x=>x.style.fontFamily==='Georgia'));
});
test('typing at a font boundary inherits the previous character, not the following span',()=>{
 const marks:TextMark[]=[{field:'option:a',start:0,end:2,style:{fontFamily:'Georgia',bold:true}},
  {field:'option:a',start:2,end:4,style:{fontFamily:'Verdana',italic:true}}];
 const after=remapMarks(marks,'option:a','ABCD','ABxyzCD');
 const parts=styledSegments('ABxyzCD',after,'option:a');
 let text='';const styles:Record<string,unknown>[]=[];
 for(const part of parts){for(const c of part.text){text+=c;styles.push(part.style)}}
 assert.equal(text,'ABxyzCD');
 for(const i of [2,3,4]){assert.equal(styles[i].fontFamily,'Georgia');assert.equal(styles[i].bold,true)}
 assert.equal(styles[5].fontFamily,'Verdana');
});
test('insertion in a styled answer and independent subquestion keeps exact previous formatting',()=>{
 for(const field of ['label','option:x','question:q:option:1']){
  const marks:TextMark[]=[{field,start:1,end:4,style:{fontFamily:'Georgia',fontSize:24,underline:true}}];
  const changed=remapMarks(marks,field,'ABCDE','ABCZZDE');
  const segments=styledSegments('ABCZZDE',changed,field);
  assert.ok(segments.some(x=>x.text.includes('ZZ')&&x.style.fontFamily==='Georgia'&&x.style.fontSize===24));
 }
});
test('format toolbar restores the highlighted DOM range following a style change',()=>{
 assert.match(main,/restoreDomTextRange\(text,range\)/);
 assert.match(main,/text\.focus\(\{preventScroll:true\}\)/);
 assert.match(main,/if\(range&&range\.end>range\.start\)/);
});
test('editor uses the same default and answer style resolution as presenter, audience and rehearsal',()=>{
 assert.match(main,/initialWidgetTextStyle\(kind\)/);
 assert.match(main,/initialWidgetTextStyle\(k\)/);
 assert.match(main,/widgetTypographyStyle\(w\.kind===/);
 assert.match(main,/answerOptionStyle\(w.style\)/);
 assert.match(main,/const format=widgetTextDefaults\(source.kind,source.style\)\|\|\{\}/);
 assert.match(css,/RC194: long answers wrap/);
 assert.match(css,/font-family:var\(--q-answer-font-family,inherit\)!important/);
});

test('insertion after a late segment inherits the actual previous character style',()=>{
 const field='option:late';
 const marks:TextMark[]=[{field,start:0,end:2,style:{fontFamily:'Arial'}},{field,start:2,end:6,style:{fontFamily:'Georgia',italic:true}}];
 assert.equal(styleOfPreviousCharacter('ABCDEF',marks,field,5).fontFamily,'Georgia');
 const after=remapMarks(marks,field,'ABCDEF','ABCDEzzF');
 const parts=styledSegments('ABCDEzzF',after,field);
 let pos=0;for(const part of parts){const end=pos+part.text.length;if(pos<=5&&end>=7){assert.equal(part.style.fontFamily,'Georgia');assert.equal(part.style.italic,true)}pos=end}
});
