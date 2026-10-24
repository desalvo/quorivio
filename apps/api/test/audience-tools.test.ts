import {test} from 'node:test';import assert from 'node:assert/strict';
import {normalizeWord,validateQuestion,moderationStatus,safeFrequency} from '../src/audience-tools.ts';
test('word cloud normalizes case and whitespace',()=>assert.equal(normalizeWord('  Great   Talk  '),'great talk'));
test('word cloud refuses unsafe/oversized inputs',()=>{assert.equal(normalizeWord('<script>'),null);assert.equal(normalizeWord('x'.repeat(49)),null);assert.equal(normalizeWord(''),null)});
test('Q&A validates length and removes edge spaces',()=>{assert.equal(validateQuestion('  What is next?  '),'What is next?');assert.equal(validateQuestion('test'),null);assert.equal(validateQuestion('x'.repeat(501)),null)});
test('moderation rejects arbitrary states',()=>{assert.equal(moderationStatus('approved'),true);assert.equal(moderationStatus('deleted'),false)});
test('word cloud has deterministic aggregation order',()=>assert.deepEqual(safeFrequency([{word:'a',count:2},{word:'c',count:5},{word:'b',count:2}]),[{word:'c',count:5},{word:'a',count:2},{word:'b',count:2}]));

test('word cloud excludes malformed or oversized aggregated labels',()=>{
 assert.deepEqual(safeFrequency([{word:'valid',count:1},{word:'',count:9},{word:'x'.repeat(49),count:5}]),[{word:'valid',count:1}]);
});
