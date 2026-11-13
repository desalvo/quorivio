import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign,publicPageDesign} from '../src/domain.ts';
const source={id:'question',kind:'question',label:'A question',answerMode:'single',options:[{id:'a',label:'A'},{id:'b',label:'B'},{id:'c',label:'C'}]};
const result={id:'result',kind:'results-button',targetWidgetId:'question'};
const chart={chartSmooth:true,chartShowPoints:false,chartShowValues:true,chartShowPercentages:true,
 chartStrokeWidth:5,chartFillOpacity:45,donutHoleSize:60,radarGridLevels:5};
test('all four chart types and editable format parameters persist in saved designs',()=>{
 for(const resultsView of ['line','area','donut','radar']){
  const page={widgets:[{...source,resultsView}, {...result,resultsView,...chart}]};
  assert.equal(validPageDesign(page),true,resultsView);
  const publicDesign=publicPageDesign(page as any);
  assert.equal(publicDesign?.widgets?.[1].resultsView,resultsView);
  assert.equal(publicDesign?.widgets?.[1].donutHoleSize,60);
  assert.equal(publicDesign?.widgets?.[1].radarGridLevels,5);
 }
});
test('invalid chart parameters, injection and unsupported widget kinds are rejected',()=>{
 for(const update of [{chartStrokeWidth:0},{chartStrokeWidth:9},{chartFillOpacity:-1},{chartFillOpacity:101},
   {donutHoleSize:19},{donutHoleSize:81},{radarGridLevels:1},{radarGridLevels:9},{chartSmooth:'true'},
   {chartShowPoints:3},{chartShowValues:null},{chartShowPercentages:'false'},{chartStrokeWidth:NaN},
   {donutHoleSize:30.2}]){
   assert.equal(validPageDesign({widgets:[source,{...result,...chart,...update}]}),false,JSON.stringify(update));
 }
 assert.equal(validPageDesign({widgets:[{id:'text',kind:'text',resultsView:'radar'}]}),false);
 assert.equal(validPageDesign({widgets:[source,{...result,resultsView:'javascript:alert(1)'}]}),false);
});
