import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign,validWidgetTextStyle} from '../src/domain.ts';
const shape=(style:unknown)=>({widgets:[{id:'pptx-shape',kind:'postit',label:'Editable shape',style}]});
test('editable PowerPoint shape outline widths persist in page design',()=>{
 for(const width of [0.25,0.5,1,2,4,8,12])assert.equal(validPageDesign(shape({strokeColor:'#aabbcc',strokeWidth:width})),true);
});
test('native PowerPoint line dashes are typed and persisted',()=>{
 for(const dash of ['solid','dash','dot'])assert.equal(validPageDesign(shape({strokeColor:'#aabbcc',strokeDash:dash})),true);
});
test('transparent fill and absent outline are explicit editable flags',()=>{
 assert.equal(validPageDesign(shape({fillNone:true,strokeNone:true})),true);
 assert.equal(validPageDesign(shape({fillNone:false,strokeNone:false,fillColor:'#abcdef'})),true);
});
test('stroke width rejects nonfinite, boolean, strings and out of bounds',()=>{
 for(const width of [-1,0,0.249,12.001,Infinity,-Infinity,NaN,true,'2',null])assert.equal(validWidgetTextStyle({strokeWidth:width}),false);
});
test('stroke dash rejects unrecognized PowerPoint enums',()=>{
 for(const dash of ['dash-dot','none','',null,0,'DASH'])assert.equal(validWidgetTextStyle({strokeDash:dash}),false);
});
test('paint flags reject string and numeric truthiness',()=>{
 for(const flag of ['true',1,null,[],{}]){
  assert.equal(validWidgetTextStyle({fillNone:flag}),false);
  assert.equal(validWidgetTextStyle({strokeNone:flag}),false);
 }
});
test('invalid colors and unknown keys remain rejected',()=>{
 assert.equal(validWidgetTextStyle({strokeColor:'red',strokeWidth:2}),false);
 assert.equal(validWidgetTextStyle({fillColor:'#00000g',fillNone:false}),false);
 assert.equal(validWidgetTextStyle({strokeDash:'dash',customXml:'<xml>'}),false);
});
