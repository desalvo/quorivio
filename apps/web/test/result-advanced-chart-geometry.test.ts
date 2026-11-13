import test from 'node:test';
import assert from 'node:assert/strict';
import {validAdvancedChartKind,cleanChartRows,chartTotal,lineChartPoints,linePath,areaPath,donutSlices,donutSlicePath,radarPoints,radarRing,radarAreaPath,chartOpacity,chartStrokeWidth,finiteChartNumber} from '../src/result-advanced-chart-geometry.ts';
const rows=[{id:'a',label:'A',count:2},{id:'b',label:'B',count:6},{id:'c',label:'C',count:2}];
test('four results chart modes are explicit; unknown modes rejected',()=>{
 for(const mode of ['line','area','donut','radar'])assert.equal(validAdvancedChartKind(mode),true);
 for(const mode of ['spline','script','bubbles',null])assert.equal(validAdvancedChartKind(mode),false);
});
test('line and filled area geometry use actual anonymous counts',()=>{
 const points=lineChartPoints(rows);assert.equal(points.length,3);
 assert.ok(points[1].y<points[0].y);assert.equal(points[0].percent,20);
 assert.match(linePath(points),/^M /);assert.match(linePath(points,true),/ C /);
 assert.match(areaPath(points),/ Z$/);assert.match(areaPath(points,true),/ C /);
 assert.deepEqual(lineChartPoints([]),[]);assert.equal(areaPath([]),'');
 assert.ok(Number.isFinite(lineChartPoints([{id:'a',label:'A',count:0}])[0].y));
});
test('donut segments are 100% total, provide real accessible counts and hole bounds',()=>{
 const slices=donutSlices(rows,55);assert.deepEqual(slices.map(s=>s.percent),[20,60,20]);
 assert.equal(slices.reduce((a,s)=>a+s.count,0),10);
 assert.ok(slices.every(s=>s.path.startsWith('M ')&&s.path.endsWith(' Z')));
 assert.equal(donutSlices(rows.map(r=>({...r,count:0}))).length,0);
 assert.equal(donutSlicePath(0,0,100,50,0,0),'');
 assert.match(donutSlices([{id:'a',label:'one',count:11}])[0].path,/ A .* A .* A .* A .* Z$/);
});
test('radar requires at least three categories and stays within finite SVG coordinates',()=>{
 const points=radarPoints(rows);assert.equal(points.length,3);
 assert.equal(radarRing(2,1),'');assert.match(radarRing(3,.5),/ Z$/);
 assert.match(radarAreaPath(points),/ Z$/);assert.equal(radarAreaPath(points.slice(0,2)),'');
 for(const p of points)assert.ok(Number.isFinite(p.x)&&Number.isFinite(p.y));
});
test('invalid counts and out-of-range configuration clamp safely',()=>{
 assert.deepEqual(cleanChartRows([{id:'a',label:'x',count:NaN},{id:'b',label:'y',count:-10}]).map(r=>r.count),[0,0]);
 assert.equal(chartTotal([{id:'a',label:'x',count:Infinity}]),0);
 assert.equal(chartOpacity(200),1);assert.equal(chartOpacity('nope'),.35);
 assert.equal(chartStrokeWidth(-2),1);assert.equal(chartStrokeWidth(Infinity),3);
 assert.equal(finiteChartNumber(undefined,20,80,55),55);
});
