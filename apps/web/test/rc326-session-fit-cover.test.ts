import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {proportionalWidgetScale,predictedResultsHeight} from '../src/widget-content-scale.ts';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
test('close session leaves only workspace; live server status is never mutated',()=>{
 const close=ui.split('function closeSidebarSession(){')[1]?.split('async function renameSidebarSession()')[0]||'';
 assert.match(close,/leaveCurrentSession\(\)/);
 assert.doesNotMatch(close,/\/status|status:'closed'|request\(/);
 assert.match(ui,/onClick=\{closeSidebarSession\} title="Chiude soltanto questa vista/);
 assert.match(ui,/session-action-terminate/);
 assert.match(ui,/onClick=\{\(\)=>changeStatus\('closed'\)\}/);
});
test('authenticated session prefetch coalesces hover and click',()=>{
 assert.match(ui,/const sessionPreviewCache=useRef/);
 assert.match(ui,/const sessionPreviewPending=useRef/);
 assert.match(ui,/onMouseEnter=\{\(\)=>warmSessionSnapshot\(s.id\)\}/);
 assert.match(ui,/onFocus=\{\(\)=>warmSessionSnapshot\(s.id\)\}/);
 assert.match(ui,/sessionPreviewPending\.current\.get\(key\)/);
 assert.match(ui,/sessionPreviewCache\.current\.clear\(\)/);
 assert.match(ui,/setSelectedSessionRole\(normalized\.session\.access_role\|\|null\)/);
 assert.match(ui,/setShowSessionLoading\(true\),550/);
});
test('automatic content fit is default and does not mutate widget geometry',()=>{
 assert.match(ui,/data-fit-mode=\{allowScale\?'scale':'scroll'\}/);
 assert.match(ui,/results\?\.dataset\.fitPredictedRows/);
 assert.match(ui,/chartHasRows/);
 assert.match(ui,/data-fit-predicted-rows=\{sourceRows\.length\}/);
 assert.match(ui,/checked=\{w\.autoFit!==false\}/);
 assert.match(ui,/autoFit is a content-fit preference, NEVER a widget geometry edit/);
 assert.doesNotMatch(ui,/Adatta automaticamente l'altezza al contenuto/);
 assert.doesNotMatch(ui,/autoFitExpandedPosition\(/);
 assert.match(css,/\[data-fit-mode="scale"\][\s\S]*?overflow:visible!important/);
});
test('scale covers natural/predicted content and honors bounds',()=>{
 assert.equal(proportionalWidgetScale({frameWidth:200,frameHeight:100,contentWidth:400,contentHeight:100}),.5);
 assert.equal(proportionalWidgetScale({frameWidth:300,frameHeight:200,contentWidth:100,contentHeight:100}),2);
 assert.equal(proportionalWidgetScale({frameWidth:300,frameHeight:200,contentWidth:100,contentHeight:100,predictedHeight:400}),.5);
 assert.equal(proportionalWidgetScale({frameWidth:0,frameHeight:200,contentWidth:100,contentHeight:100}),1);
 assert.equal(predictedResultsHeight({rows:5,maxRowHeight:32,otherHeight:80,truthBadge:true}),260);
});
test('login reuses bundled manual cover without external image requests',()=>{
 assert.match(ui,/className="hero login-manual-cover"/);
 assert.match(css,/url\('\/docs\/assets\/quorivio-manual-cover\.png'\)/);
 assert.match(css,/rgba\(8,12,29/);
});

test('RC327: extreme and predicted content never exceeds either widget dimension',()=>{
 const extreme={frameWidth:160,frameHeight:90,contentWidth:1_000_000,contentHeight:100,minScale:.08};
 const reduced=proportionalWidgetScale(extreme);
 assert.ok(reduced<.005,'automatic fit must override a minimum that would clip content');
 assert.ok(reduced*extreme.contentWidth<=extreme.frameWidth);
 assert.ok(reduced*extreme.contentHeight<=extreme.frameHeight);
 const forecast=proportionalWidgetScale({frameWidth:300,frameHeight:180,contentWidth:90,contentHeight:40,predictedWidth:750,predictedHeight:900});
 assert.equal(forecast,.2);
 const enlarged=proportionalWidgetScale({frameWidth:300,frameHeight:200,contentWidth:10,contentHeight:10});
 assert.equal(enlarged,20,'small content can occupy the maximal available dimension');
 const capped=proportionalWidgetScale({frameWidth:300,frameHeight:200,contentWidth:10,contentHeight:10,maxScale:3});
 assert.equal(capped,3,'a specialized renderer may explicitly cap upscaling');
 assert.equal(proportionalWidgetScale({frameWidth:300,frameHeight:200,contentWidth:Infinity,contentHeight:10}),1);
 assert.doesNotMatch(ui,/maxScale:2\\.25/,'default content fit must not impose an arbitrary enlargement cap');
 assert.match(ui,/setFactor\\(previous=>next<previous\\?next:/,'growth in natural content must immediately reduce scale');
});
