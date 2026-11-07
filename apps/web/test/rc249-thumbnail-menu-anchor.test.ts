/** RC249: a floating thumbnail menu never intercepts its own toggle, including
 * when scrolling/zooming causes the original trigger rectangle to move. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {thumbnailMenuPosition} from '../src/thumbnail-menu-layout.ts';

const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const intersects=(a:{left:number;top:number;right:number;bottom:number}, b:{left:number;top:number;right:number;bottom:number})=>
 a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;

test('menu always stays in the viewport and completely off its live trigger',()=>{
 for(const [vw,vh] of [[320,240],[390,380],[390,844],[760,820],[960,760],[1440,900]]){
  for(const triggerLeft of [8, Math.round(vw*.35), Math.max(8,vw-45)]){
   for(const triggerTop of [8,Math.round(vh*.43),Math.max(8,vh-48)]){
    const anchor={left:triggerLeft,right:triggerLeft+32,top:triggerTop,bottom:triggerTop+32};
    const p=thumbnailMenuPosition(anchor.right+8,anchor.top,vw,vh,anchor);
    const popup={left:p.left,top:p.top,right:p.left+p.width,bottom:p.top+p.maxHeight};
    assert.ok(p.width>0 && p.maxHeight>0,{vw,vh,p});
    assert.ok(p.left>=8-1 && p.top>=8-1 && popup.right<=vw-8+1 && popup.bottom<=vh-8+1,{vw,vh,p});
    assert.equal(intersects(anchor,popup),false,JSON.stringify({vw,vh,anchor,p}));
   }
  }
 }
});

test('scroll and resize re-anchor the open body portal while leaving accessible menu actions intact',()=>{
 assert.match(main,/getBoundingClientRect\(\)/);
 assert.match(main,/window\.addEventListener\('scroll',reposition,true\)/);
 assert.match(main,/window\.addEventListener\('resize',reposition\)/);
 assert.match(main,/visualViewport\?\.addEventListener\('resize',reposition\)/);
 assert.match(main,/setPageMenuPosition\(thumbnailMenuPosition\(/);
 assert.match(main,/--thumbnail-menu-width/);
 assert.match(main,/setPageThumbMenu\(''\);return/);
 assert.match(css,/width:var\(--thumbnail-menu-width,min\(270px,calc\(100vw - 16px\)\)\)!important/);
 assert.match(main,/page-editor-thumb-menu-floating/);
 assert.match(main,/aria-expanded=\{pageThumbMenu===a.id\}/);
});
