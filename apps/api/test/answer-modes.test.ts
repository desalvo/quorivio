import {test} from 'node:test';import {strict as assert} from 'node:assert';import {validAnswerMode,validateSubmittedAnswer,validReaction} from '../src/domain.ts';
const opts=[{id:'a',label:'A'},{id:'b',label:'B'}];
test('quiz modes',()=>{for(const mode of ['single','multiple','text','file'])assert.ok(validAnswerMode(mode));assert.equal(validAnswerMode('unsafe'),false)});
test('single option',()=>{assert.deepEqual(validateSubmittedAnswer('single',true,'a',opts)?.optionIds,['a']);assert.equal(validateSubmittedAnswer('single',true,'x',opts),null)});
test('multiple distinct options',()=>{assert.deepEqual(validateSubmittedAnswer('multiple',true,['a','b'],opts)?.optionIds,['a','b']);assert.equal(validateSubmittedAnswer('multiple',true,['a','a'],opts),null)});
test('open text',()=>{assert.equal(validateSubmittedAnswer('text',true,'answer',opts)?.text,'answer');assert.equal(validateSubmittedAnswer('text',true,'',opts),null);assert.ok(validateSubmittedAnswer('text',false,'',opts))});
test('file UUID validation',()=>{assert.equal(validateSubmittedAnswer('file',true,'nope',opts),null);assert.ok(validateSubmittedAnswer('file',true,'123e4567-e89b-42d3-a456-426614174000',opts))});
test('reaction whitelist',()=>{assert.equal(validReaction('👍'),true);assert.equal(validReaction('bad'),false)});
