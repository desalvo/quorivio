import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign} from '../src/domain.ts';

const title={id:'schema-title',kind:'title',label:'Schema',titleUseMaster:true,
 style:{fillNone:true,strokeNone:true,shapeType:'rectangle'},
 position:{x:8,y:3,width:84,height:12,rotation:0}};
const footer={id:'schema-footer',kind:'footer',footerShowPageNumber:true,
 position:{x:0,y:87,width:100,height:13,rotation:0}};
test('persist a valid session scheme with title and footer',()=>{
 assert.equal(validPageDesign({master:{titleStyle:{fontFamily:'Arial',fontSize:38},widgets:[title,footer]}}),true);
});
test('reject duplicate scheme types, non-scheme widgets and invalid geometry',()=>{
 assert.equal(validPageDesign({master:{widgets:[title,{...title,id:'other'}]}}),false);
 assert.equal(validPageDesign({master:{widgets:[{...title,kind:'question'}]}}),false);
 assert.equal(validPageDesign({master:{widgets:[{...footer,position:{x:0,y:95,width:100,height:13,rotation:0}}]}}),false);
 assert.equal(validPageDesign({master:{widgets:[{...title,label:'<script>alert(1)</script>',style:{fontSize:999}}]}}),false);
});
test('reject undeclared scheme properties and preserve legacy titleStyle-only schemes',()=>{
 assert.equal(validPageDesign({master:{titleStyle:{fontFamily:'Georgia',fontSize:45}}}),true);
 assert.equal(validPageDesign({master:{widgets:[],arbitraryValue:true}}),false);
});
