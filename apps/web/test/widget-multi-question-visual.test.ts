import test from 'node:test';import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {sampleStatisticRows,rowsFromWidgetAnswerDetail} from '../src/widget-results.ts';
const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const rich=readFileSync(new URL('../src/widget-rich-editor.tsx',import.meta.url),'utf8');
test('separate answer keys and plain-text rich editing are shared by editor, audience and rehearsal',()=>{
 assert.match(main,/question_id:questionId/);
 assert.match(main,/QuestionWidgetSingle/);
 assert.match(main,/function ProjectedQuestionPart/);
 assert.match(main,/function WidgetSubquestionEditor/);
 assert.match(main,/editContent\(w,'question:'\+q.id/);
 assert.match(main,/function SessionRehearsal/);
 assert.match(rich,/contentEditable=\{active\}/);
 assert.match(rich,/styledSegments\(value,marks,field\)/);
 assert.match(rich,/onPaste=\{e=>\{e.preventDefault\(\)/);
 assert.doesNotMatch(rich,/dangerouslySetInnerHTML/);
});
test('linked results use independent subquestion data, not parent option labels',()=>{
 const source={id:'a',kind:'question',options:[{id:'parent',label:'Parent'}],questions:[{id:'sub1',label:'Child',options:[{id:'one',label:'One'},{id:'two',label:'Two'}]}]};
 const a=sampleStatisticRows(source,98,{'a:sub1':'two'},'sub1');
 const b=sampleStatisticRows(source,98,{},'sub1');
 assert.deepEqual(a.map(r=>r.id),['one','two']);
 assert.equal(a[1].count,b[1].count+1);
 assert.equal(rowsFromWidgetAnswerDetail(source,{revisions:[{options:{one:2,two:4}}]},'sub1')[1].count,4);
 assert.deepEqual(sampleStatisticRows(source,98,{},'missing'),[]);
});
