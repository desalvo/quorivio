import assert from 'node:assert/strict';
import test from 'node:test';
import {contextWidgetIndex,canvasWidgetAtPoint} from '../src/editor-context-hit.ts';

test('native context on the visible widget rectangle routes to widget, not background',()=>{
 const rects=[{left:100,top:100,right:250,bottom:200},{left:220,top:140,right:300,bottom:230}];
 assert.equal(contextWidgetIndex(rects,130,125),0);
 assert.equal(contextWidgetIndex(rects,230,150),1);
 assert.equal(contextWidgetIndex(rects,10,10),-1);
 assert.equal(contextWidgetIndex(rects,130,250),-1);
});
test('context hit respects viewport pixels and exact rectangle edges',()=>{
 const rects=[{left:0,top:0,right:100,bottom:50}];
 assert.equal(contextWidgetIndex(rects,0,0),0);
 assert.equal(contextWidgetIndex(rects,100,50),0);
 assert.equal(contextWidgetIndex(rects,NaN,10),-1);
});
test('DOM canvas lookup handles pointer interception and empty background',()=>{
 const widgets=[
  {getBoundingClientRect:()=>({left:4,top:4,right:40,bottom:40})},
  {getBoundingClientRect:()=>({left:50,top:50,right:80,bottom:80})},
 ];
 const canvas={querySelectorAll:()=>widgets} as unknown as HTMLElement;
 assert.equal(canvasWidgetAtPoint(canvas,20,20),widgets[0]);
 assert.equal(canvasWidgetAtPoint(canvas,60,60),widgets[1]);
 assert.equal(canvasWidgetAtPoint(canvas,45,45),null);
});
