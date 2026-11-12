import test from 'node:test';import assert from 'node:assert/strict';
import {eligibleStatisticSources,linkedStatisticSource,sampleStatisticRows,topicQuestionRows,rowsFromWidgetAnswerDetail,gaugeModel,gaugeColor,effectiveResultView} from '../src/widget-results.ts';
const page=[{id:'q1',kind:'question',label:'Domanda',options:[{id:'a',label:'A'},{id:'b',label:'B'}]},{id:'r1',kind:'rating'},{id:'rx',kind:'reactions'},{id:'stat',kind:'results-button',targetWidgetId:'q1'},{id:'text',kind:'text'}];
test('statistics sources are scoped to eligible peer widgets on the same page',()=>{assert.deepEqual(eligibleStatisticSources(page,'stat').map(w=>w.id),['q1','r1','rx']);assert.equal(linkedStatisticSource(page[3],page)?.id,'q1');assert.equal(linkedStatisticSource({...page[3],targetWidgetId:'text'},page),undefined);assert.equal(linkedStatisticSource({...page[3],targetWidgetId:'absent'},page),undefined)});
test('preview sample is stable for one opening and changes with seed',()=>{const a=sampleStatisticRows(page[0],42),b=sampleStatisticRows(page[0],42);assert.deepEqual(a,b);assert.notDeepEqual(a,sampleStatisticRows(page[0],45));assert.equal(sampleStatisticRows(page[0],42,{q1:'a'})[0].count,a[0].count+1)});
test('preview sample supports all reactions and 0-9 ratings',()=>{assert.equal(sampleStatisticRows(page[1],1).length,10);assert.equal(sampleStatisticRows(page[2],1).length,8)});
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

test('RC313 Gauge rating histogram uses 0-9 range and weighted votes',()=>{
 const rows=[{id:'0',label:'0',count:1},{id:'9',label:'9',count:3}];
 const mean=gaugeModel(rows,{},'rating');
 assert.equal(mean.value,6.75);assert.equal(mean.min,0);assert.equal(mean.max,9);
 assert.equal(mean.percent,75);assert.equal(mean.total,4);
 assert.equal(gaugeModel(rows,{gaugeAggregation:'min'},'rating').value,0);
 assert.equal(gaugeModel(rows,{gaugeAggregation:'max'},'rating').value,9);
});
test('RC313 auto/manual limits and invalid or empty histogram',()=>{
 const bins=[{id:'a',label:'alpha',count:2},{id:'b',label:'beta',count:8}];
 assert.equal(gaugeModel(bins,{}).value,5);
 assert.equal(gaugeModel(bins,{}).max,8);
 assert.equal(gaugeModel(bins,{gaugeMinMode:'manual',gaugeMin:2,gaugeMaxMode:'manual',gaugeMax:6}).percent,75);
 assert.equal(gaugeModel(bins,{gaugeMinMode:'manual',gaugeMin:10,gaugeMaxMode:'manual',gaugeMax:5}).max,11);
 assert.equal(gaugeModel([],{},'rating').value,null);
 assert.equal(gaugeModel([{id:'x',label:'NaN',count:3}],{}).value,3);
 assert.equal(gaugeColor('javascript:invalid'),'#000000');
});
test('RC313 linked results use the source chart by default, allow explicit override',()=>{
 const source={id:'q',kind:'rating',resultsView:'pie'};
 assert.equal(effectiveResultView({id:'r',kind:'results-button',targetWidgetId:'q'},[source]),'pie');
 assert.equal(effectiveResultView({id:'r',kind:'results-button',targetWidgetId:'q',resultsView:'gauge'},[source]),'gauge');
});

test('RC316 Gauge shares the graduated needle dial across editor, rehearsal and live without empty vertical area',async()=>{
 const {readFileSync}=await import('node:fs');
 const {fileURLToPath}=await import('node:url');
 const {resolve,dirname}=await import('node:path');
 const base=resolve(dirname(fileURLToPath(import.meta.url)),'../src');
 const main=readFileSync(resolve(base,'main.tsx'),'utf8');
 const css=readFileSync(resolve(base,'style.css'),'utf8');
 assert.match(main,/className="linked-results-gauge-needle"/);
 assert.match(main,/length:51/);
 assert.match(main,/viewBox="0 0 360 286"/);
 assert.match(main,/effectiveResultView\(w,widgets\)==='gauge'/);
 assert.match(main,/p\.height>desired\+1/);
 assert.match(css,/\.linked-results\.result-view-gauge \.[\s\S]*?max-height:none!important/);
 assert.match(css,/\.linked-results-gauge-fill\{fill:none;stroke-width:20/);
 assert.equal(gaugeModel([{id:'1',label:'3',count:1},{id:'2',label:'5',count:1}],{},'rating').value,4);
});
