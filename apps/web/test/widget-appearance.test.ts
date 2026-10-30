import test from 'node:test';
import assert from 'node:assert/strict';
import {widgetAppearanceStyle} from '../src/widget-appearance.ts';
test('explicit background and border styles are consistent for canvas presenter and audience',()=>{
 assert.deepEqual(widgetAppearanceStyle({fillColor:'#efefef',strokeColor:'#123456',strokeWidth:3,strokeDash:'dash',rounded:true}),{backgroundColor:'#efefef',backgroundImage:'none',borderStyle:'dashed',borderColor:'#123456',borderWidth:'3pt',borderRadius:14,clipPath:undefined});
});
test('transparent widget with no border overrides the default theme',()=>{
 const result=widgetAppearanceStyle({fillNone:true,strokeNone:true});
 assert.equal(result.backgroundColor,'transparent');assert.equal(result.backgroundImage,'none');assert.equal(result.borderStyle,'none');assert.equal(result.borderWidth,0);
});
test('no chosen appearance leaves the theme in control',()=>{
 assert.deepEqual(widgetAppearanceStyle(undefined),{});
 assert.equal(widgetAppearanceStyle({strokeDash:'dot'}).borderStyle,'dotted');
 assert.equal(widgetAppearanceStyle({shapeType:'ellipse'}).borderRadius,'50%');
});
