import test from 'node:test';
import assert from 'node:assert/strict';
import {formatSelectedOrEntireField,scaleAllWidgetTypography,applyAllWidgetTypeface,styledSegments} from '../src/widget-text-marks.ts';

test('whole-widget scaling retains different label, option, inline and submit sizes',()=>{
 const current={style:{fontSize:24,answerFontSize:16,submitButtonSize:18},textMarks:[{field:'label',start:0,end:5,style:{fontSize:32}},{field:'option:1',start:0,end:2,style:{fontSize:12}}]};
 const next=scaleAllWidgetTypography(current,1.25);
 assert.equal(next.style.fontSize,30);assert.equal(next.style.answerFontSize,20);assert.equal(next.style.submitButtonSize,23);
 assert.equal(next.textMarks[0].style.fontSize,40);assert.equal(next.textMarks[1].style.fontSize,15);
 assert.equal(current.textMarks[0].style.fontSize,32);
});
test('size scale bounds preserve server limits',()=>{
 const result=scaleAllWidgetTypography({style:{fontSize:96,answerFontSize:10},textMarks:[{field:'label',start:0,end:2,style:{fontSize:96}}]},1.5);
 assert.equal(result.style.fontSize,96);assert.equal(result.style.answerFontSize,15);assert.equal(result.textMarks[0].style.fontSize,96);
});
test('field format changes only its field and respects highlighted ranges',()=>{
 const existing=[{field:'option:1',start:0,end:3,style:{color:'#008800'}}];
 const title=formatSelectedOrEntireField(existing,'label','Titolo',null,{fontFamily:'Georgia'});
 assert.equal(title.find(m=>m.field==='label')?.end,6);
 assert.equal(title.find(m=>m.field==='option:1')?.style.color,'#008800');
 const onlyRange=formatSelectedOrEntireField(title,'label','Titolo',{start:1,end:3},{color:'#224466'});
 const parts=styledSegments('Titolo',onlyRange,'label');
 assert.equal(parts.map(x=>x.text).join(''),'Titolo');
 assert.equal(parts[1].style.color,'#224466');
});
test('applying a face to whole widget updates answer font and existing inline runs',()=>{
 const updated=applyAllWidgetTypeface({style:{fontFamily:'Arial',answerColor:'#334455'},textMarks:[{field:'option:1',start:0,end:3,style:{fontFamily:'Verdana',fontSize:22}}]}, {fontFamily:'Georgia',color:'#123456'});
 assert.equal(updated.style.answerFontFamily,'Georgia'); assert.equal(updated.style.answerColor,'#123456');
 assert.equal(updated.textMarks[0].style.fontFamily,'Georgia'); assert.equal(updated.textMarks[0].style.fontSize,22);
});
