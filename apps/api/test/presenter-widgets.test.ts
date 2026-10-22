import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign} from '../src/domain.ts';
const user='123e4567-e89b-42d3-a456-426614174000';
test('multiple ratings with independent widget IDs',()=>assert.equal(validPageDesign({widgets:[{id:'rate-question',kind:'rating',label:'Valutazione',targetKind:'question'},{id:'rate-presenter',kind:'rating',label:'Valutazione',targetKind:'presenter',targetId:user}]}),true));
test('multiple presenter profile widgets',()=>assert.equal(validPageDesign({widgets:[{id:'profile-1',kind:'profile',presenterId:user},{id:'profile-2',kind:'profile'}]}),true));
test('reject invalid widget identity or target',()=>{assert.equal(validPageDesign({widgets:[{id:'profile-1',kind:'profile',presenterId:'../../invalid'}]}),false);assert.equal(validPageDesign({widgets:[{id:'r',kind:'rating',label:'Valutazione',targetKind:'arbitrary'}]}),false)});
test('removal of widget preserves remaining validation',()=>{const widgets=[{id:'a',kind:'rating'},{id:'b',kind:'profile'}];assert.equal(validPageDesign({widgets:widgets.filter(w=>w.id!=='a')}),true)});
