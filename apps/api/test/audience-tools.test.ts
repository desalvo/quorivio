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

import {parseModerationQueueQuery} from '../src/audience-tools.ts';
test('moderation defaults to pending queue at page one',()=>assert.deepEqual(parseModerationQueueQuery(undefined,undefined),{status:'pending',page:1,offset:0}));
test('moderation accepts explicit approved, rejected and all filters',()=>{
 for(const status of ['pending','approved','rejected','all'])assert.deepEqual(parseModerationQueueQuery(status,'2'),{status,page:2,offset:20});
});
test('moderation supports final accepted page without unbounded offset',()=>{
 assert.deepEqual(parseModerationQueueQuery('all','10000'),{status:'all',page:10000,offset:199980});
});
test('moderation rejects invalid states',()=>{
 for(const status of ['',null,false,1,{},['pending'],'deleted','PENDING','__proto__'])assert.equal(parseModerationQueueQuery(status,'1'),null);
});
test('moderation rejects negative, float, zero and nondecimal page numbers',()=>{
 for(const page of ['-1','0','1.0','1e1',' 1','1 ','+2','0x10','10001','9999999','abc','1;DROP',false,null,{},['1']])assert.equal(parseModerationQueueQuery('pending',page),null);
});
test('moderation only accepts safe, bounded decimal page values',()=>{
 for(const page of ['1','9','10','999','1000','9999'])assert.equal(parseModerationQueueQuery('all',page)?.page,Number(page));
});

import {parseModerationBulk} from '../src/audience-tools.ts';
const QA_IDS=['11111111-1111-4111-8111-111111111111','22222222-2222-4222-8222-222222222222'];
test('bulk moderation accepts one or two distinct UUIDs and allowed statuses',()=>{
 for(const status of ['approved','rejected'])assert.deepEqual(parseModerationBulk({status,ids:QA_IDS}),{status,ids:QA_IDS});
});
test('bulk moderation rejects malformed, empty and oversized selections',()=>{
 for(const ids of [[],[1],['not-uuid'],[QA_IDS[0],QA_IDS[0]],Array(21).fill(QA_IDS[0]),'uuid',null])assert.equal(parseModerationBulk({status:'approved',ids}),null);
});
test('bulk moderation rejects untrusted status and payload prototypes',()=>{
 for(const status of ['pending','deleted','all',null,1])assert.equal(parseModerationBulk({status,ids:QA_IDS}),null);
 for(const body of [null,undefined,0,false,'json',[],{}])assert.equal(parseModerationBulk(body),null);
});
