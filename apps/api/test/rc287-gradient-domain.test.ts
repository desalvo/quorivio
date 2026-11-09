import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign} from '../src/domain.ts';
const base={widgets:[{id:'result-1',kind:'results-button',label:'Risultati',barHitGradient:true}]};
test('author-selected result gradient colors persist through strict schema validation',()=>{
 assert.equal(validPageDesign({...base,widgets:[{...base.widgets[0],barGradientStartColor:'#021ABC',barGradientEndColor:'#ad53c0'}]}),true);
});
test('invalid hex, unsafe text, and unrelated widget colors are rejected',()=>{
 for(const value of ['#gggggg','red','linear-gradient(red, blue)','#1234','transparent',42]){
  assert.equal(validPageDesign({...base,widgets:[{...base.widgets[0],barGradientStartColor:value}]}),false,String(value));
 }
 assert.equal(validPageDesign({widgets:[{id:'text-1',kind:'text',barGradientStartColor:'#ff0000'}]}),false);
});
