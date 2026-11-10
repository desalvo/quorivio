import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign,publicPageDesign} from '../src/domain.ts';

const widget={id:'results-1',kind:'results-button',label:'Risultati',resultsView:'pie',pieShowPercentages:true};

test('persist pie sizes 40 through 100 without changing the result source',()=>{
 for(const pieSize of [40,50,72,85,100]){
  const design={widgets:[{...widget,pieSize}]};
  assert.equal(validPageDesign(design),true,String(pieSize));
  assert.equal(publicPageDesign(design as any)?.widgets?.[0].pieSize,pieSize);
 }
});
test('legacy result widgets without pie size remain valid',()=>{
 assert.equal(validPageDesign({widgets:[widget]}),true);
});
test('reject unsafe, out-of-range, fractional and unrelated widget pie sizes',()=>{
 for(const pieSize of [-1,0,20,39,40.1,100.1,101,Infinity,NaN,'75',null]){
  assert.equal(validPageDesign({widgets:[{...widget,pieSize}]}),false,String(pieSize));
 }
 assert.equal(validPageDesign({widgets:[{id:'text-1',kind:'text',label:'Hello',pieSize:75}]}),false);
});
