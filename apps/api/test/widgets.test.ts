import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign} from '../src/domain.ts';
test('widget palette accepts ordered widgets',()=>assert.equal(validPageDesign({widgets:[{id:'rating-1',kind:'rating',label:'Soddisfazione'},{id:'text-1',kind:'text',label:'Hello'}]}),true));
test('reject invalid and duplicated widget identifiers',()=>{assert.equal(validPageDesign({widgets:[{id:'a',kind:'rating'},{id:'a',kind:'rating'}]}),false);assert.equal(validPageDesign({widgets:[{id:'x',kind:'script'}]}),false)});
test('reject oversized widget labels',()=>assert.equal(validPageDesign({widgets:[{id:'a',kind:'text',label:'x'.repeat(241)}]}),false));
