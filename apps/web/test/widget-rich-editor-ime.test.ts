import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {styledSegments,remapMarks} from '../src/widget-text-marks.ts';
const editor=readFileSync(new URL('../src/widget-rich-editor.tsx',import.meta.url),'utf8');
test('IME composition buffers intermediate browser events rather than rebuilding styled spans',()=>{
 assert.match(editor,/onCompositionStart=\{\(\)=>\{composing\.current=true\}\}/);
 assert.match(editor,/onInput=\{e=>\{if\(lock\.current\|\|composing\.current\)return/);
 assert.match(editor,/onCompositionEnd=\{e=>\{composing\.current=false/);
 assert.match(editor,/!composing\.current&&\(e\.key==='Enter'/);
});
test('Unicode UTF-16 selection offsets remain consistent through formatting and insertion',()=>{
 const text='A😀B'; // emoji is two UTF-16 code units
 const marks=[{field:'label',start:1,end:3,style:{bold:true}}];
 assert.deepEqual(styledSegments(text,marks,'label').map(x=>[x.text,x.style.bold??false]),[['A',false],['😀',true],['B',false]]);
 const expanded=remapMarks(marks,'label','A😀B','A😀!B');
 assert.equal(expanded[0].start,1);
 assert.equal(expanded[0].end,3);
});
test('different independent question fields never inherit marks from another question',()=>{
 const marks=[{field:'question:q1:label',start:0,end:4,style:{color:'#ff0000'}},
              {field:'question:q2:label',start:0,end:4,style:{color:'#0000ff'}}];
 assert.equal(styledSegments('Test',marks,'question:q1:label')[0].style.color,'#ff0000');
 assert.equal(styledSegments('Test',marks,'question:q2:label')[0].style.color,'#0000ff');
 assert.equal(styledSegments('Test',marks,'label')[0].style.color,undefined);
});
