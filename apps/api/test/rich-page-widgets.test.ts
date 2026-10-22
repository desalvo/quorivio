import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign,validWidgetTextStyle} from '../src/domain.ts';
test('rating title is mandatory and description optional',()=>{
 assert.equal(validPageDesign({widgets:[{id:'rating1',kind:'rating'}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'rating1',kind:'rating',label:'Valuta la sessione',description:'Puoi aggiungere un commento'}]}),true);
});
test('multiple mixed widgets and editable question settings',()=>{
 assert.equal(validPageDesign({widgets:[{id:'q1',kind:'question',label:'Domanda A',answerMode:'multiple'},{id:'q2',kind:'question',label:'Domanda B',answerMode:'text'},{id:'t1',kind:'text',label:'Introduzione'}]}),true);
});
test('restrict font, color, size, and animation',()=>{
 assert.equal(validWidgetTextStyle({fontFamily:'Georgia',fontSize:32,color:'#aabbcc',bold:true,italic:true,underline:true,strikethrough:false,animation:'fade'}),true);
 for (const style of [{fontFamily:'evil'}, {fontSize:1000},{color:'javascript:alert(1)'},{animation:'unknown'},{bold:'true'}])assert.equal(validWidgetTextStyle(style),false);
});
