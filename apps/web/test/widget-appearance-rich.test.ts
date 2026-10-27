import test from 'node:test';
import assert from 'node:assert/strict';
import {widgetAppearanceStyle} from '../src/widget-appearance.ts';
test('gradient and opacity apply to background, not to text',()=>{
 const s=widgetAppearanceStyle({fillMode:'gradient',fillOpacity:0.5,fillColor:'#123456',gradientEndColor:'#aabbcc'});
 assert.match(String(s.backgroundImage),/linear-gradient/);assert.match(String(s.backgroundImage),/#12345680/);assert.equal(s.opacity,undefined);
});
test('private image fills are not displayed without a trusted URL',()=>{
 const s={fillMode:'image' as const,fillImageAssetId:'88'};
 assert.equal(widgetAppearanceStyle(s).backgroundImage,undefined);
 assert.equal(widgetAppearanceStyle(s,'/api/sessions/session-id/assets/88').backgroundImage,'url("/api/sessions/session-id/assets/88")');
});
test('vector border shapes have individually visible silhouettes',()=>{
 for(const shapeType of ['triangle','diamond','hexagon','cloud','speech'] as const)assert.match(String(widgetAppearanceStyle({shapeType}).clipPath),/polygon\(/);
 assert.equal(widgetAppearanceStyle({shapeType:'circle'}).borderRadius,'50%');
});
