import test from 'node:test';
import assert from 'node:assert/strict';
import {validWidgetPosition,validPageDesign} from '../src/domain.ts';
test('validates normalized canvas positions',()=>{
 for(const pos of [{x:0,y:0,width:100},{x:52,y:72,width:48},{x:1.5,y:22.5,width:30}])assert.equal(validWidgetPosition(pos),true);
 for(const pos of [{x:90,y:10,width:20},{x:-1,y:0,width:50},{x:0,y:99,width:50},{x:0,y:0,width:0},{x:0,y:0,width:100,unsafe:true},{x:NaN,y:1,width:80},{x:'0',y:0,width:50}])assert.equal(validWidgetPosition(pos),false);
});
test('canvas coordinates are accepted in heterogeneous page widget layouts',()=>{
 assert.equal(validPageDesign({widgets:[{id:'abc',kind:'text',label:'Hello',position:{x:0,y:0,width:45}},{id:'def',kind:'question',label:'Q',position:{x:49,y:12,width:50}}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'abc',kind:'text',position:{x:95,y:0,width:50}}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'abc',kind:'text'}]}),true);
});
