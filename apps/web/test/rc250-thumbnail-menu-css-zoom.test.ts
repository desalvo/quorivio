/** RC250: native DOMRect hit coordinates must be converted back from root CSS zoom
 * when positioning a fixed menu portaled under document.body. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {thumbnailMenuPosition} from '../src/thumbnail-menu-layout.ts';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const workflow=readFileSync(new URL('../../../.github/workflows/ci.yml',import.meta.url),'utf8');

const overlaps=(a:{left:number;top:number;right:number;bottom:number},b:{left:number;top:number;right:number;bottom:number})=>
 a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top;

test('CSS zoom returns layout offsets that display beside the real physical trigger',()=>{
 for(const [vw,vh] of [[320,240],[390,844],[760,720],[960,760],[1440,940]]){
  for(const scale of [.64,.8,1,1.2]){
   for(const x of [90,180,290]){
    const trigger={left:x*scale,top:96*scale,right:(x+34)*scale,bottom:130*scale};
    if(trigger.right>vw-8)continue;
    const p=thumbnailMenuPosition(trigger.right+8,trigger.top,vw,vh,trigger,scale);
    // A menu attached to a CSS-zoomed root renders p.* multiplied by scale.
    const visible={left:p.left*scale,top:p.top*scale,
      right:(p.left+p.width)*scale,bottom:(p.top+p.maxHeight)*scale};
    assert.equal(overlaps(trigger,visible),false,JSON.stringify({vw,vh,scale,trigger,p,visible}));
    assert.ok(visible.left>=7&&visible.right<=vw-7&&visible.top>=7&&visible.bottom<=vh-7);
   }
  }
 }
});

test('negative reproduction: legacy uncorrected position physically hits trigger at 80% zoom',()=>{
 const scale=.8,trigger={left:240,top:96,right:267.2,bottom:123.2};
 const legacy=thumbnailMenuPosition(trigger.right+8,trigger.top,1440,940,trigger);
 const oldVisible={left:legacy.left*scale,top:legacy.top*scale,
   right:(legacy.left+legacy.width)*scale,bottom:(legacy.top+legacy.maxHeight)*scale};
 assert.equal(overlaps(trigger,oldVisible),true);
 const corrected=thumbnailMenuPosition(trigger.right+8,trigger.top,1440,940,trigger,scale);
 const fixedVisible={left:corrected.left*scale,top:corrected.top*scale,
   right:(corrected.left+corrected.width)*scale,bottom:(corrected.top+corrected.maxHeight)*scale};
 assert.equal(overlaps(trigger,fixedVisible),false);
});

test('live DOM zoom feeds open and reposition, with root observer and full editor CI retained',()=>{
 assert.equal((ui.match(/Number\.parseFloat\(getComputedStyle\(document\.documentElement\)\.zoom\)\|\|1/g)||[]).length,2);
 assert.match(ui,/event\.anchor,rootZoom/);
 assert.match(ui,/bottom:rect\.bottom\},rootZoom/);
 assert.match(ui,/MutationObserver\(reposition\)/);
 assert.match(ui,/zoomObserver\.disconnect\(\)/);
 assert.match(workflow,/python3 tools\/ci_rc250_thumbnail_zoom_chromium\.py/);
 assert.match(workflow,/python3 tools\/ci_browser_editor\.py/);
});
