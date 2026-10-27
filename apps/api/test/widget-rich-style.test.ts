import assert from 'node:assert/strict';
import test from 'node:test';
import {validWidgetTextStyle,validPageDesign} from '../src/domain.ts';
import {referencedAssets,remapPortableAssets} from '../src/portable-bundle.ts';
const id='8e763f69-9915-4591-b561-177322052709';
const page=(style:any)=>({widgets:[{id:'w1',kind:'text',label:'Welcome',style,position:{x:5,y:8,width:26,height:20}}]});
test('multiple vector borders and alpha/gradient styles are strictly validated',()=>{
 for(const shapeType of ['rectangle','rounded-rectangle','ellipse','circle','triangle','diamond','cloud','speech','hexagon']){
  assert.equal(validWidgetTextStyle({shapeType,fillMode:'gradient',fillColor:'#123456',gradientEndColor:'#eeeeee',fillOpacity:0.45,strokeWidth:3.5}),true,shapeType);
  assert.equal(validPageDesign(page({shapeType,fillMode:'solid',fillOpacity:0.7})),true,shapeType);
 }
 for(const bad of [{shapeType:'script'},{fillOpacity:1.1},{fillOpacity:-1},{fillOpacity:NaN},{fillMode:'url(http)'},{fillImageAssetId:'../../hello'},{gradientEndColor:'url(http)'},{ratingView:'hidden'}])assert.equal(validWidgetTextStyle(bad),false);
});
test('an image fill is a first-class private bundle asset and receives a new ID',()=>{
 const source={format:'quorivio-session',version:1,session:{theme:{}},activities:[{page_design:page({fillMode:'image',fillImageAssetId:id}),result_design:{}}]};
 assert.deepEqual([...referencedAssets(source)],[id]);
 const imported=remapPortableAssets(source,[id]);
 const after=imported.definition.activities[0].page_design.widgets[0].style.fillImageAssetId;
 assert.notEqual(after,id);assert.equal(after,imported.ids.get(id));assert.equal(source.activities[0].page_design.widgets[0].style.fillImageAssetId,id);
});

test('participant count and results view persist through the authoritative API schema',()=>{
 assert.equal(validPageDesign({widgets:[{id:'connected',kind:'participant-count',style:{fillMode:'gradient',fillOpacity:0.5,gradientEndColor:'#123456'}}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'stats',kind:'results-button',resultsView:'cloud',style:{fillMode:'image',fillImageAssetId:id}}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'stats',kind:'results-button',resultsView:'javascript'}]}),false);
});
