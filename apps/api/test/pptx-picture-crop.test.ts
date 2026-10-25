import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign,validPictureCrop} from '../src/domain.ts';
const crop={left:0.15,right:0.1,top:0.2,bottom:0.05};
const assetId='123e4567-e89b-42d3-a456-426614174000';
test('PowerPoint crop fractions are typed and bounded',()=>{
 assert.equal(validPictureCrop(crop),true);
 assert.equal(validPictureCrop({left:0,right:0,top:0,bottom:0}),true);
 assert.equal(validPictureCrop({left:0.95,right:0,top:0,bottom:0}),true);
});
test('image and logo may persist native editable crop metadata',()=>{
 for(const kind of ['image','logo'])assert.equal(validPageDesign({widgets:[{id:'pic',kind,assetId,crop}]}),true);
});
test('non-image widgets reject crop metadata',()=>{
 for(const kind of ['text','postit','pdf','video'])assert.equal(validPageDesign({widgets:[{id:'pic',kind,crop}]}),false);
});
test('malformed, nonfinite and overcropped pictures rejected',()=>{
 for(const bad of [{...crop,left:0.95,right:0.1},{...crop,top:0.9,bottom:0.2},{...crop,left:NaN},{...crop,right:Infinity},{...crop,top:-0.1},{...crop,bottom:'0.2'},{...crop,extra:0},{left:0},null,[],{}]){
  assert.equal(validPictureCrop(bad),false);
  assert.equal(validPageDesign({widgets:[{id:'pic',kind:'image',assetId,crop:bad}]}),false);
 }
});
