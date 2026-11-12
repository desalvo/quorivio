import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const workflow=readFileSync(new URL('../../../.github/workflows/ci.yml',import.meta.url),'utf8');
const browser=readFileSync(new URL('../../../tools/ci_rc306_bar_wrap_chromium.py',import.meta.url),'utf8');

test('RC326 supersedes RC306 scroll-only bars with one bounded proportional fit',()=>{
 assert.ok(ui.includes("const chartHasRows=Boolean(results&&['bars','pie','table','cloud'].includes("));
 assert.ok(ui.includes('const next=proportionalWidgetScale({'));
 assert.ok(ui.includes('contentWidth:Math.max(b.scrollWidth,b.clientWidth)'));
 assert.ok(ui.includes('contentHeight:Math.max(b.scrollHeight,b.clientHeight)'));
 assert.ok(ui.includes("data-fit-mode={allowScale?'scale':'scroll'}"));
 assert.ok(ui.includes("data-fit-predicted-rows={sourceRows.length}"));
 assert.ok(css.includes('RC326: the entire authored widget scales together'));
});
test('RC306 result label widths are bounded and long words wrap naturally',()=>{
 assert.ok(css.includes('RC306 — Long statistics options'));
 const block=css.slice(css.indexOf('/* RC306 — Long statistics options'));
 for(const fragment of ['.linked-result-label{','.linked-result-final{','.linked-result-pair{','.linked-results-track{',
   'display:inline!important;white-space:normal!important;',
   'overflow-wrap:anywhere!important;word-break:normal!important;',
   'width:100%!important;max-width:100%!important;min-width:0!important;']){
  assert.ok(block.includes(fragment),fragment);
 }
 assert.ok(block.includes('overflow-x:hidden!important;overflow-y:auto!important;'));
});
test('RC306 dedicated Chromium test measures actual multiline label geometry',()=>{
 assert.ok(workflow.includes('python3 tools/ci_rc306_bar_wrap_chromium.py'));
 assert.ok(browser.includes('getClientRects()'));
 assert.ok(browser.includes('getComputedStyle'));
 assert.ok(browser.includes('scrollWidth'));
 assert.ok(browser.includes('viewport'));
});

test('RC308 source question titles honor the authored/default font size on every results chart',()=>{
 assert.ok(ui.includes("fontSize:`${Math.max(10,Math.min(96,Number(format.fontSize)||22))}px`"));
 assert.ok(ui.includes('function LinkedResultChart('));
 assert.ok(ui.includes('<LinkedResultSourceQuestion result={viewWidget} source={source} rankedRows={data}/>'));
 assert.ok(css.includes('.linked-results>.linked-source-question{font-size:inherit}'));
});
test('RC308 QR URL typography is configurable and independent of QR image resizing',()=>{
 const domain=readFileSync(new URL('../../api/src/domain.ts',import.meta.url),'utf8');
 assert.ok(ui.includes('ariaLabel="Dimensione font URL QRCode"'));
 assert.ok(ui.includes("qrUrlFontSize:next,qrUrlWidthExtra:"));
 assert.ok(ui.includes("'--qr-url-extra-width'"));
 assert.ok(css.includes('font-size:var(--qr-url-font-size,15px)!important'));
 assert.ok(css.includes('max-width:min(var(--qr-image-size,100%),max(0px,calc(100% - var(--qr-url-extra-width,0px))))!important'));
 assert.ok(css.includes('max-height:min(100%,var(--qr-image-size,100%))!important'));
 assert.ok(ui.includes("'--qr-image-size':Number.isFinite(widget.qrImagePixels)"));
 assert.ok(domain.includes('qrUrlFontSize?:number;qrUrlWidthExtra?:number;qrImagePixels?:number'));
 assert.ok(domain.includes('w.qrUrlFontSize>=10&&w.qrUrlFontSize<=96'));
});
