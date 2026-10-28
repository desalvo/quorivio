import test from 'node:test';import assert from 'node:assert/strict';
import {eligibleStatisticSources,linkedStatisticSource,sampleStatisticRows,topicQuestionRows,rowsFromWidgetAnswerDetail} from '../src/widget-results.ts';
const page=[{id:'q1',kind:'question',label:'Domanda',options:[{id:'a',label:'A'},{id:'b',label:'B'}]},{id:'r1',kind:'rating'},{id:'rx',kind:'reactions'},{id:'stat',kind:'results-button',targetWidgetId:'q1'},{id:'text',kind:'text'}];
test('statistics sources are scoped to eligible peer widgets on the same page',()=>{assert.deepEqual(eligibleStatisticSources(page,'stat').map(w=>w.id),['q1','r1','rx']);assert.equal(linkedStatisticSource(page[3],page)?.id,'q1');assert.equal(linkedStatisticSource({...page[3],targetWidgetId:'text'},page),undefined);assert.equal(linkedStatisticSource({...page[3],targetWidgetId:'absent'},page),undefined)});
test('preview sample is stable for one opening and changes with seed',()=>{const a=sampleStatisticRows(page[0],42),b=sampleStatisticRows(page[0],42);assert.deepEqual(a,b);assert.notDeepEqual(a,sampleStatisticRows(page[0],45));assert.equal(sampleStatisticRows(page[0],42,{q1:'a'})[0].count,a[0].count+1)});
test('preview sample supports all reactions and 0-10 ratings',()=>{assert.equal(sampleStatisticRows(page[1],1).length,11);assert.equal(sampleStatisticRows(page[2],1).length,8)});
test('real aggregated response revisions map by source option id',()=>{assert.deepEqual(rowsFromWidgetAnswerDetail(page[0],{revisions:[{options:{a:2}},{options:{a:1,b:4}}]}).map(x=>x.count),[3,4])});

test('scoped presenter topic statistics have a real count and no participant PII',()=>{
 const topic={id:'topic1',kind:'topic-question',label:'Questions'};
 assert.deepEqual(eligibleStatisticSources([...page,topic]).map(w=>w.id),['q1','r1','rx','topic1']);
 assert.equal(linkedStatisticSource({id:'rt',kind:'results-button',targetWidgetId:'topic1'},[...page,topic])?.id,'topic1');
 assert.deepEqual(topicQuestionRows(10),[{id:'topic-count',label:'Domande ricevute',count:10}]);
 assert.deepEqual(topicQuestionRows(-1),topicQuestionRows('10'));
 const demo=sampleStatisticRows(topic,19,{},'',{topic1:2})[0];
 assert.equal(demo.count,sampleStatisticRows(topic,19)[0].count+2);
 assert.equal(sampleStatisticRows(topic,19)[0].count,sampleStatisticRows(topic,19)[0].count);
});
