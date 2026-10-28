import test from 'node:test';import assert from 'node:assert/strict';import {validPageDesign} from '../src/domain.ts';
const q={id:'q',kind:'question',label:'Preferenza',answerMode:'single',options:[{id:'a',label:'A'},{id:'b',label:'B'}]};
const result={id:'result',kind:'results-button',targetWidgetId:'q',resultsView:'bars'};
test('each results widget references an eligible widget on the same page',()=>{
 assert.equal(validPageDesign({widgets:[q,result]}),true);
 assert.equal(validPageDesign({widgets:[q,{...result,id:'result2'},result]}),true);
 for(const id of ['result','missing','text'])assert.equal(validPageDesign({widgets:[q,{...result,targetWidgetId:id},{id:'text',kind:'text'}]}),false);
 assert.equal(validPageDesign({widgets:[{...result,targetWidgetId:undefined}]}),true); // legacy migration
 assert.equal(validPageDesign({widgets:[{id:'text',kind:'text'},result]}),false);
});
