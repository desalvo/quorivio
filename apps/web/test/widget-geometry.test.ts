import test from 'node:test';import assert from 'node:assert/strict';
import {widgetGeometryStyle} from '../src/widget-geometry.ts';
test('editor presenter and audience share identical percentage layout',()=>{
 const pos={x:12.5,y:20,width:65.5,height:31,rotation:-30};
 assert.deepEqual(widgetGeometryStyle(pos),{position:'absolute',left:'12.5%',top:'20%',width:'65.5%',height:'31%',transform:'rotate(-30deg)'});
});
test('zero rotation is retained and omitted height falls back consistently',()=>{
 assert.deepEqual(widgetGeometryStyle({x:0,y:0,width:100,rotation:0}),{position:'absolute',left:'0%',top:'0%',width:'100%',height:'24%',transform:'rotate(0deg)'});
});
