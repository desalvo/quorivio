import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resultBarGradient,DEFAULT_BAR_GRADIENT_START,DEFAULT_BAR_GRADIENT_END} from '../src/result-bar-gradient.ts';
const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('configurable result-bar gradient interpolates both author colors by response share',()=>{
 assert.equal(resultBarGradient('#ff0000','#0000ff',0),'linear-gradient(90deg, #ff0000, #ff0000)');
 assert.equal(resultBarGradient('#ff0000','#0000ff',1),'linear-gradient(90deg, #ff0000, #0000ff)');
 assert.equal(resultBarGradient('#ff0000','#0000ff',.5),'linear-gradient(90deg, #ff0000, #800080)');
 assert.equal(resultBarGradient('invalid','#bad',2),`linear-gradient(90deg, ${DEFAULT_BAR_GRADIENT_START}, ${DEFAULT_BAR_GRADIENT_END})`);
 assert.equal(resultBarGradient('#ff0000','#0000ff',NaN),'linear-gradient(90deg, #ff0000, #ff0000)');
});

test('Format widget exposes two color pickers and persists each result widget setting',()=>{
 assert.match(main,/aria-label="Colore iniziale gradiente barre"/);
 assert.match(main,/aria-label="Colore finale gradiente barre"/);
 assert.match(main,/patch\(w\.id,\{barGradientStartColor:e\.target\.value\}\)/);
 assert.match(main,/patch\(w\.id,\{barGradientEndColor:e\.target\.value\}\)/);
 assert.match(main,/resultBarGradient\(widget\.barGradientStartColor,widget\.barGradientEndColor/);
});

test('the authoring canvas has no footer-overlapping truth switch, R remains interactive',()=>{
 assert.doesNotMatch(main,/className="canvas-results-truth-toggle"/);
 assert.match(main,/className=\{'result-answer-key-toggle'/);
 assert.match(main,/setTruthVisible\(v=>!v\)/);
});

test('graded frames have enough internal spacing, independent row spacing, and no overlapping outlines',()=>{
 assert.match(css,/\.linked-source-answers\{gap:clamp\(7px/);
 assert.match(css,/\.linked-results-items\{row-gap:clamp\(7px/);
 assert.match(css,/\.widget-answer-option\[data-answer-verdict\],\.linked-results-row\[data-answer-verdict\]\{/);
 assert.match(css,/border-width:3px!important;border-style:solid!important/);
 assert.match(css,/min-height:max-content!important;height:auto!important/);
 assert.match(css,/overflow-wrap:anywhere!important;white-space:pre-wrap!important/);
});

test('resized formatting window retains explicit width/height and scrolls on every tab',()=>{
 assert.match(main,/\x27--editor-floating-height\x27:size\.height\+\x27px\x27/);
 assert.match(main,/setFormatTab\(id as typeof formatTab\)/);
 assert.match(css,/\.widget-selection-palette\{\s*display:flex!important;flex-direction:column!important/);
 assert.match(css,/\.palette-ribbon-groups\[role="tabpanel"\]\{\s*flex:1 1 0%!important;min-height:0!important;max-height:none!important/);
});

test('mock-inspired sidebar has actual Lucide icons and accessible current-page state',()=>{
 assert.match(main,/className="panel dashboard-nav"/);
 assert.match(main,/<Icon size=\{18\} aria-hidden="true"\/>/);
 assert.match(main,/aria-current=\{dashboardPage===key\?'page':undefined\}/);
 assert.match(css,/\.dashboard>\.aside \.dashboard-nav \.session\.selected/);
 assert.match(css,/background:linear-gradient\(100deg,#0c816f,#0c705f\)/);
});
