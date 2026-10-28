import test from 'node:test';
import assert from 'node:assert/strict';
import {changedRegion,formatTextRange,remapMarks,styledSegments,inlineMarkCss,type TextMark} from '../src/widget-text-marks.ts';

test('selected text is styled without affecting adjacent characters',()=>{
 const marks=formatTextRange([],'label',5,10,{bold:true,color:'#123456'});
 assert.deepEqual(styledSegments('HelloWorldAgain',marks,'label').map(p=>[p.text,p.style.bold??null]),[['Hello',null],['World',true],['Again',null]]);
 assert.equal(inlineMarkCss(marks[0].style).color,'#123456');
});
test('styled text never accepts HTML as markup and preserves literal characters',()=>{
 const chunks=styledSegments('<img src=x>',[{field:'label',start:1,end:4,style:{italic:true}}],'label');
 assert.equal(chunks.map(x=>x.text).join(''),'<img src=x>');
});
test('a character-range mark only affects its intended option',()=>{
 const marks=formatTextRange([],'option:o1',1,3,{fontFamily:'Georgia'});
 assert.equal(styledSegments('Choice',marks,'option:o2').length,1);
 assert.equal(styledSegments('Choice',marks,'option:o1').length,3);
});
test('inserted text in styled run extends the mark',()=>{
 const before:TextMark[]=[{field:'label',start:2,end:6,style:{underline:true}}];
 assert.deepEqual(remapMarks(before,'label','ABCDEFG','ABCxxDEFG'),[{field:'label',start:2,end:8,style:{underline:true}}]);
});
test('editing one field does not shift marks for another',()=>{
 const marks:TextMark[]=[{field:'option:o1',start:1,end:4,style:{color:'#ffffff'}}];
 assert.deepEqual(remapMarks(marks,'label','Old','Updated'),marks);
});
test('removed character ranges discard empty marks',()=>{
 const marks:TextMark[]=[{field:'label',start:1,end:3,style:{bold:true}}];
 assert.deepEqual(remapMarks(marks,'label','ABCD','AD'),[]);
});
test('changes at selected insertion caret are identified',()=>{
 assert.deepEqual(changedRegion('Hello','HelXlo'),{start:3,end:4});
 assert.deepEqual(changedRegion('Hello','Hello!'),{start:5,end:6});
});
test('oversized ranges never enter the UI state',()=>{
 assert.deepEqual(formatTextRange([],'label',10,510,{italic:true}),[]);
 assert.deepEqual(formatTextRange([],'label',4,4,{italic:true}),[]);
});

test('editing a short field preserves a long unrelated choice mark',()=>{
 const marks:TextMark[]=[{field:'option:long',start:20,end:37,style:{bold:true}}];
 assert.deepEqual(remapMarks(marks,'label','Untitled','Hi'),marks);
});
test('editing or removing a choice only changes marks assigned to that choice',()=>{
 const marks:TextMark[]=[{field:'option:x',start:3,end:8,style:{italic:true}},{field:'option:y',start:8,end:15,style:{underline:true}}];
 const edited=remapMarks(marks,'option:x','abcdefghij','abcd');
 assert.deepEqual(edited.filter(m=>m.field==='option:y'),[marks[1]]);
 assert.ok(edited.every(m=>m.field!=='option:x'||m.end<=4));
});
