import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const workflow=readFileSync(new URL('../../../.github/workflows/ci.yml',import.meta.url),'utf8');
const browser=readFileSync(new URL('../../../tools/ci_rc306_bar_wrap_chromium.py',import.meta.url),'utf8');

test('RC306 detects bar chart children and avoids auto-fit shrinking the entire widget',()=>{
 assert.ok(ui.includes("b.querySelector('.linked-results.result-view-bars')"));
 assert.ok(ui.includes('if(hasBars){setFactor(1);return;}'));
 assert.ok(ui.includes("const canScale=allowScale&&!readableBars;"));
 assert.ok(ui.includes("data-fit-mode={canScale?'scale':'scroll'}"));
 assert.ok(ui.includes("transform:canScale&&factor<.985?"));
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
