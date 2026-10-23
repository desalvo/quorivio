import test from 'node:test';
import assert from 'node:assert/strict';
import {validWidgetPosition,validPageDesign} from '../src/domain.ts';
test('validates normalized canvas positions',()=>{
 for(const pos of [{x:0,y:0,width:100},{x:52,y:72,width:48},{x:1.5,y:22.5,width:30}])assert.equal(validWidgetPosition(pos),true);
 for(const pos of [{x:90,y:10,width:20},{x:-1,y:0,width:50},{x:0,y:100,width:50},{x:0,y:0,width:0},{x:0,y:0,width:100,unsafe:true},{x:NaN,y:1,width:80},{x:'0',y:0,width:50}])assert.equal(validWidgetPosition(pos),false);
});
test('canvas coordinates are accepted in heterogeneous page widget layouts',()=>{
 assert.equal(validPageDesign({widgets:[{id:'abc',kind:'text',label:'Hello',position:{x:0,y:0,width:45}},{id:'def',kind:'question',label:'Q',position:{x:49,y:12,width:50}}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'abc',kind:'text',position:{x:95,y:0,width:50}}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'abc',kind:'text'}]}),true);
});

test('rotation and independent topic widgets',()=>{assert.equal(validWidgetPosition({x:10,y:10,width:40,height:30,rotation:37.5}),true);assert.equal(validWidgetPosition({x:10,y:10,width:40,height:30,rotation:Infinity}),false);assert.equal(validWidgetPosition({x:10,y:10,width:40,height:30,rotation:361}),false);assert.equal(validPageDesign({widgets:[{id:'topic1',kind:'topic-question',label:'Topic 1',showNames:false,position:{x:2,y:5,width:48,height:38,rotation:-28}}]}),true);});

 test('small imported PPTX objects retain faithful geometry',()=>{assert.equal(validWidgetPosition({x:71,y:52,width:2.5,height:1.5}),true);assert.equal(validWidgetPosition({x:99.5,y:98.8,width:0.5,height:1.2}),true);assert.equal(validWidgetPosition({x:90,y:90,width:11,height:2}),false);});
