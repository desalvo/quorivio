import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {widgetAppearanceStyle,widgetShapeOutline} from '../src/widget-appearance.ts';
import {floatingWidgetMenuPosition} from '../src/editor-context-menu.ts';
import {validWidgetTextStyle} from '../../api/src/domain.ts';

const polygons=['triangle','diamond','hexagon','cloud','speech'] as const;
test('0pt outline is valid and is the default, even with existing stroke color',()=>{
 for(const style of [undefined,{strokeColor:'#334155'},{strokeWidth:0,strokeColor:'#334155'},
  {strokeWidth:0,strokeDash:'dash' as const,shapeType:'diamond' as const}]){
  const paint=widgetAppearanceStyle(style);
  assert.equal(paint.borderWidth,0);
  assert.equal(paint.borderStyle,'none');
  assert.equal(widgetShapeOutline(style),null);
 }
 assert.equal(validWidgetTextStyle({strokeWidth:0}),true);
 assert.equal(validWidgetTextStyle({strokeWidth:-0.01}),false);
 assert.equal(validWidgetTextStyle({strokeWidth:12.1}),false);
 assert.equal(validWidgetTextStyle({strokeWidth:0.25}),true);
});

test('each nonrectangular shape gets vector outline when border is nonzero',()=>{
 for(const shapeType of polygons){
  const style={shapeType,strokeColor:'#112233',strokeWidth:2,strokeDash:'dot' as const,fillNone:true};
  const paint=widgetAppearanceStyle(style);
  assert.match(String(paint.clipPath),/^polygon/);
  assert.equal(paint.borderStyle,'none');
  assert.equal(paint.borderWidth,0);
  const edge=widgetShapeOutline(style);
  assert.ok(edge?.path.startsWith('M '));
  assert.ok(edge?.path.endsWith(' Z'));
  assert.equal(edge?.color,'#112233');
  assert.equal(edge?.width,2);
  assert.equal(edge?.dash,'dot');
  assert.equal(widgetShapeOutline({...style,strokeNone:true}),null);
 }
 assert.equal(widgetShapeOutline({strokeWidth:2,shapeType:'rectangle'}),null);
 assert.equal(widgetAppearanceStyle({strokeWidth:2,shapeType:'rounded-rectangle'}).borderWidth,'2pt');
});

test('floating menu avoids the widget on both sides and near viewport edges',()=>{
 const viewport={width:1440,height:900};
 for(const rect of [{left:100,top:150,right:300,bottom:300},
                    {left:1140,top:120,right:1390,bottom:270},
                    {left:600,top:700,right:790,bottom:870}]){
  const pos=floatingWidgetMenuPosition(rect,viewport.width,viewport.height);
  assert.ok(pos.x>=8&&pos.x<=1192);
  assert.ok(pos.y>=8&&pos.y<=462);
  const overlap=Math.max(0,Math.min(pos.x+240,rect.right)-Math.max(pos.x,rect.left))*
                Math.max(0,Math.min(pos.y+430,rect.bottom)-Math.max(pos.y,rect.top));
  assert.equal(overlap,0,`menu should not cover widget at ${JSON.stringify(rect)}: ${JSON.stringify(pos)}`);
 }
});

test('svg overlay is wired to the four slide surfaces, and context menu remains portaled',()=>{
 const src=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
 const matches=src.match(/<WidgetShapeOutline style=\{w\.style\}\/>/g)||[];
 assert.equal(matches.length,5);
 assert.match(src,/floatingWidgetMenuPosition\(rect,window\.innerWidth,window\.innerHeight,y\)/);
 assert.match(src,/contextWidget===w\.id&&createPortal\(<div className="canvas-context-menu"/);
 assert.match(css,/\.widget-vector-outline\{position:absolute!important/);
});
