import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const chrome=readFileSync(new URL('../../../tools/ci_browser_participant.py',import.meta.url),'utf8');

test('rating textarea in accessible reading mode has an explicit 44 CSS px minimum',()=>{
 const rule=css.match(/\.audience-widget-layout\.stage-reading>\.page-widget textarea\.rating-comment-input\s*\{([^}]+)\}/);
 assert.ok(rule,'required accessible rating field rule');
 assert.match(rule[1],/min-height:\s*44px!important/);
 const legacy=css.indexOf('min-height:3em!important');
 assert.ok(legacy>=0&&css.indexOf(rule[0])>legacy,'reading override must follow scaled control');
 assert.match(chrome,/assert reading\['fieldHeight'\]>=44/);
});
test('faithful 16:9 slide preserves authored compact rating control',()=>{
 assert.match(css,/textarea\.rating-comment-input\s*\{[^}]*min-height:3em!important/s);
 assert.doesNotMatch(css,/\.audience-widget-layout\.stage-fidelity>\.page-widget textarea\.rating-comment-input\s*\{[^}]*min-height:\s*44px/s);
});
