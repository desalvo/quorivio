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

test('transparent fill hides a selected private image but preserves the independent border',()=>{
 const style={fillMode:'image' as const,fillNone:true,strokeColor:'#334155',fillImageAssetId:'8e763f69-9915-4591-b561-177322052709'};
 const result=widgetAppearanceStyle(style,'/api/sessions/s1/assets/8e763f69-9915-4591-b561-177322052709');
 assert.equal(result.backgroundImage,'none');
 assert.equal(result.backgroundColor,'transparent');
 assert.equal(result.borderColor,'#334155');
});
