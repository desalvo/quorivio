import assert from 'node:assert/strict';
import test from 'node:test';
import {validPageDesign} from '../src/domain.ts';
test('RC73 accepts title and footer widgets plus a valid session slide master',()=>{
 assert.equal(validPageDesign({widgets:[{id:'page-title',kind:'title',label:'Pagina uno',titleFollowPage:true,titleUseMaster:true,style:{fillNone:true,shapeType:'rectangle'},position:{x:8,y:3,width:84,height:12,rotation:0}},{id:'footer',kind:'footer',footerShowSessionTitle:true,footerShowPageNumber:true,style:{fillNone:true},position:{x:0,y:94,width:100,height:6,rotation:0}}]}),true);
 assert.equal(validPageDesign({master:{titleStyle:{fontFamily:'Georgia',fontSize:48,bold:true,color:'#AABBCC',textAlign:'center'}}}),true);
});
test('RC73 rejects malformed master properties and footer-only settings on other kinds',()=>{
 assert.equal(validPageDesign({master:{titleStyle:{fontSize:999}}}),false);
 assert.equal(validPageDesign({master:{unknown:'x'}}),false);
 assert.equal(validPageDesign({widgets:[{id:'f',kind:'footer',footerShowPageNumber:'true'}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'q',kind:'question',footerShowPageNumber:true}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'t',kind:'title',titleUseMaster:'yes'}]}),false);
});
