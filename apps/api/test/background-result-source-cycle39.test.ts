import {test} from 'node:test';
import assert from 'node:assert/strict';
import {effectiveResultView,linkedStatisticSource} from '../../web/src/widget-results.ts';

test('source question controls linked result rendering regardless of stale result-widget setting',()=>{
 const source={id:'poll-1',kind:'question',resultsView:'cloud',label:'Poll'};
 const result={id:'out-1',kind:'results-button',targetWidgetId:'poll-1',resultsView:'pie'};
 assert.equal(linkedStatisticSource(result,[source,result])?.id,'poll-1');
 assert.equal(effectiveResultView(result,[source,result]),'cloud');
});
test('source visualization can change without changing the linked result widget',()=>{
 const source={id:'quiz',kind:'timed-quiz',resultsView:'pie'};
 const result={id:'out',kind:'results-button',targetWidgetId:'quiz'};
 assert.equal(effectiveResultView(result,[source,result]),'pie');
 source.resultsView='table';
 assert.equal(effectiveResultView(result,[source,result]),'table');
});
test('unlinked or invalid result displays fail to accessible bars fallback',()=>{
 const result={id:'out',kind:'results-button',targetWidgetId:'missing',resultsView:'cloud'};
 assert.equal(effectiveResultView(result,[result]),'bars');
 assert.equal(effectiveResultView({...result,targetWidgetId:'a'},[{id:'a',kind:'reactions',resultsView:'unknown'},result]),'bars');
});
