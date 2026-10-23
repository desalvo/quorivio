import test from 'node:test';import assert from 'node:assert/strict';import {validTransition,validateOptions,checkAnswer,publicActivity,escapeCsvCell,validRetentionDays} from '../src/domain.ts';
test('closed sessions cannot reopen',()=>{assert.equal(validTransition('closed','active'),false);assert.equal(validTransition('draft','active'),true)});
test('options must be unique and valid',()=>{assert.equal(validateOptions([{id:'x',label:'A'},{id:'x',label:'B'}]),false);assert.equal(validateOptions([{id:'x',label:'A'},{id:'y',label:'B'}]),true)});
test('quiz answers checked exclusively server-side',()=>{assert.equal(checkAnswer({type:'quiz',correct_option_id:'y',options:[]},'x'),false);assert.equal(checkAnswer({type:'quiz',correct_option_id:'y',options:[]},'y'),true)});
test('correct answer must not leak into participant activity',()=>{assert.equal('correct_option_id' in publicActivity({id:'x',session_id:'s',type:'quiz',title:'?',options:[],correct_option_id:'secret',duration_seconds:null,status:'open',position:0}),false)});

test('CSV output neutralizes formula injection',()=>{for(const value of ['=1+1','  @SUM(A1)','+cmd','-2'])assert.equal(escapeCsvCell(value).startsWith('"\''),true);assert.equal(escapeCsvCell('hello "there"'),'"hello ""there"""')});
test('retention day validation is bounded',()=>{assert.equal(validRetentionDays(90),true);for(const value of [0,-1,3651,2.5,'90'])assert.equal(validRetentionDays(value),false)});

import {validPageDesign,validPseudonym} from '../src/domain.ts';
test('page design supports typed visual assets without inline HTML',()=>{
 assert.equal(validPageDesign({logos:['https://assets.example.org/logo.svg'],media:[{kind:'pdf',url:'https://assets.example.org/agenda.pdf'}]}),true);
 assert.equal(validPageDesign({header:'Hello',css:'body{display:none}'}),false);
 assert.equal(validPageDesign({backgroundUrl:'javascript:alert(1)'}),false);
});
test('anonymous pseudonyms are bounded and reject markup',()=>{
 assert.equal(validPseudonym('Guest 12'),true);
 assert.equal(validPseudonym('<script>'),false);
 assert.equal(validPseudonym('x'),false);
});

// Uploaded backgrounds must be UUID references, never arbitrary local paths.
assert.equal(validPageDesign({backgroundAssetId:'not-a-uuid'}),false);
assert.equal(validPageDesign({backgroundAssetId:'123e4567-e89b-42d3-a456-426614174000'}),true);
