import test from 'node:test';import assert from 'node:assert/strict';
import {movePageId} from '../src/page-order.ts';
test('moving a page preserves stable identifiers',()=>assert.deepEqual(movePageId(['a','b','c','d'],'a','c'),['b','c','a','d']));
test('moving backwards preserves remaining order',()=>assert.deepEqual(movePageId(['a','b','c'],'c','a'),['c','a','b']));
test('dropping on self is no-op',()=>assert.deepEqual(movePageId(['a','b'],'a','a'),['a','b']));
test('reject unknown or duplicate identifiers',()=>{assert.throws(()=>movePageId(['a','b'],'x','a'));assert.throws(()=>movePageId(['a','a'],'a','a'))});
