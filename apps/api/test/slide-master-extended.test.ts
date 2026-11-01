import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign} from '../src/domain.ts';
const foot={id:'f',kind:'footer',label:'',footerShowPageNumber:true,footerNumberX:75,footerNumberY:40,footerSeparator:false,footerSeparatorColor:'#aabbcc',position:{x:0,y:93,width:100,height:7,rotation:0}};
test('validate new footer number position and independent separator',()=>{
 assert.equal(validPageDesign({master:{widgets:[foot]}}),true);
 for(const bad of [-1,101,Infinity,NaN,'50'])assert.equal(validPageDesign({master:{widgets:[{...foot,footerNumberX:bad}]}}),false);
 assert.equal(validPageDesign({master:{widgets:[{...foot,footerSeparatorColor:'red'}]}}),false);
});
test('generic scheme widgets can be saved, duplicate title/footer cannot',()=>{
 const base={id:'a',kind:'text',label:'Hello'};
 assert.equal(validPageDesign({master:{widgets:[base,{id:'b',kind:'text',label:'Again'},foot]}}),true);
 assert.equal(validPageDesign({master:{widgets:[foot,{...foot,id:'f2'}]}}),false);
});
