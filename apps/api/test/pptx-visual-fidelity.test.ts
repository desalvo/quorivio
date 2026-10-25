import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign, validWidgetTextStyle} from '../src/domain.ts';

test('solid slide backgrounds accept exactly opaque RGB',()=>{
 for(const color of ['#000000','#FFFFFF','#12ab34'])assert.equal(validPageDesign({backgroundColor:color}),true);
 for(const color of ['red','#0000','#11223344','url(https://evil.test)','transparent',42,null])assert.equal(validPageDesign({backgroundColor:color}),false);
});
test('solid background coexists with image backgrounds and widgets',()=>{
 assert.equal(validPageDesign({backgroundColor:'#AABBCC',backgroundAssetId:'123e4567-e89b-42d3-a456-426614174000',widgets:[{id:'a',kind:'text',label:'A'}]}),true);
});
test('horizontal alignment accepts only known safe values',()=>{
 for(const value of ['left','center','right'])assert.equal(validWidgetTextStyle({textAlign:value}),true);
 for(const value of ['justify','inherit','start',null,0])assert.equal(validWidgetTextStyle({textAlign:value}),false);
});
test('vertical alignment accepts only known safe values',()=>{
 for(const value of ['top','middle','bottom'])assert.equal(validWidgetTextStyle({verticalAlign:value}),true);
 for(const value of ['baseline','stretch',null,0])assert.equal(validWidgetTextStyle({verticalAlign:value}),false);
});
test('alignment styles persist in typed page designs',()=>{
 assert.equal(validPageDesign({widgets:[{id:'aligned',kind:'text',style:{textAlign:'right',verticalAlign:'middle'}}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'bad',kind:'text',style:{textAlign:'justify'}}]}),false);
});
test('visual fidelity style cannot smuggle CSS or extra fields',()=>{
 assert.equal(validWidgetTextStyle({textAlign:'left',verticalAlign:'top',position:'absolute'}),false);
 assert.equal(validPageDesign({backgroundColor:'#123456',css:'*{display:none}'}),false);
});
