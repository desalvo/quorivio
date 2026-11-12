import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fitReactionBubbleLayout,reactionBubbles} from '../src/widget-results.ts';
import {validPageDesign} from '../../api/src/domain.ts';

const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('RC321 Gauge defaults to white with dark accessible captions and optional transparency',()=>{
 assert.match(css,/\.linked-results\.result-view-gauge\{\s*background:#fff!important;color:#182b45!important/);
 assert.match(css,/\.linked-results\.result-view-gauge\[data-gauge-transparent="true"\]\{background:transparent!important\}/);
 assert.match(css,/\.linked-results-gauge-value\{fill:#142945/);
 assert.match(css,/\.linked-results-gauge-major text\{fill:#1c304b/);
 assert.match(main,/gaugeTransparent===true/);
 assert.match(main,/onChange=\{e=>patch\(w\.id,\{gaugeTransparent:e\.target\.checked\}\)\}/);
 assert.equal(validPageDesign({widgets:[{id:'r',kind:'reactions',resultsView:'gauge',gaugeTransparent:true}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'r',kind:'reactions',resultsView:'gauge',gaugeTransparent:'yes'}]}),false);
});
test('RC321 bubble fit is the default, persists, and can return to scroll mode',()=>{
 assert.match(main,/checked=\{w\.bubbleNoScroll!==false\}/);
 assert.match(main,/onChange=\{e=>patch\(w\.id,\{bubbleNoScroll:e\.target\.checked\}\)\}/);
 assert.match(main,/fit=\{\(widget\.bubbleNoScroll\?\?source\.bubbleNoScroll\)!==false\}/);
 assert.match(css,/\.linked-results\.result-view-bubbles\[data-bubbles-fit="true"\]/);
 assert.match(main,/new ResizeObserver\(measure\)/);
 assert.match(main,/reactionBubbles\(rows,widget\.resultTopCount\?\?rows\.length/);
 assert.equal(validPageDesign({widgets:[{id:'reaction',kind:'reactions',bubbleNoScroll:false}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'reaction',kind:'reactions',bubbleNoScroll:1}]}),false);
});
test('RC321 responsive grid keeps every reaction inside resize-constrained cells',()=>{
 const items=reactionBubbles(['👍','❤️','😂','😮','👏','🎉','🤔','😕'].map((label,i)=>({id:String(i),label,count:i+1})),8);
 for(const [width,height] of [[640,300],[300,160],[180,95],[100,60],[60,35]]){
  const layout=fitReactionBubbleLayout(items,width,height);
  assert.ok(layout.columns*layout.rows>=items.length);
  assert.equal(layout.diameters.length,items.length);
  assert.ok(layout.diameters.every(d=>Number.isFinite(d)&&d>0&&d<=layout.diameter));
  assert.ok(layout.cellWidth*layout.columns<=width+1);
  assert.ok(layout.cellHeight*layout.rows<=height+1);
 }
 const large=fitReactionBubbleLayout(items,640,300);
 const small=fitReactionBubbleLayout(items,160,95);
 assert.ok(small.diameter<large.diameter);
 assert.ok(small.metaFont<large.metaFont);
});
