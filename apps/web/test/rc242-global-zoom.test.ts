import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeGlobalZoom,nextGlobalZoom,zoomStyleValue,GLOBAL_ZOOM_MIN,GLOBAL_ZOOM_MAX} from '../src/global-page-zoom.ts';

test('zoom defaults to 100 percent for corrupt, empty or unsafe persisted state',()=>{
 for(const v of [null,undefined,'',NaN,Infinity,'<script>','not-a-number'])assert.equal(normalizeGlobalZoom(v),100);
});
test('zoom increments in steps of ten, never outside accessible range',()=>{
 assert.equal(nextGlobalZoom(100,-1),90);
 assert.equal(nextGlobalZoom(100,1),110);
 assert.equal(nextGlobalZoom(GLOBAL_ZOOM_MIN,-1),GLOBAL_ZOOM_MIN);
 assert.equal(nextGlobalZoom(GLOBAL_ZOOM_MAX,1),GLOBAL_ZOOM_MAX);
 assert.equal(normalizeGlobalZoom(-900),GLOBAL_ZOOM_MIN);
 assert.equal(normalizeGlobalZoom(1000),GLOBAL_ZOOM_MAX);
});
test('normal zoom restores the original document scaling',()=>{
 assert.equal(zoomStyleValue(100),'80%');
 assert.equal(zoomStyleValue(120),'96%');
 assert.equal(zoomStyleValue(80),'64%');
});
