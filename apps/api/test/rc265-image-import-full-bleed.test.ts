import test from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {validPageDesign} from '../src/domain.ts';

const uid=randomUUID();
for(const mode of ['contain','cover','fill'] as const){
 test(`imported ${mode} raster page is valid, including scheme visibility`,()=>{
  for(const suppressMaster of [true,false])assert.equal(validPageDesign({backgroundAssetId:uid,backgroundColor:'#ffffff',importedImageFit:mode,suppressMaster,widgets:[]}),true);
 });
}
test('imported image background cannot be a network URL without an asset',()=>{
 assert.equal(validPageDesign({importedImageFit:'cover',backgroundUrl:'https://example.org/p.png',widgets:[]}),false);
 assert.equal(validPageDesign({backgroundAssetId:'../../etc',importedImageFit:'cover',widgets:[]}),false);
});
test('legacy pages and normal scheme-bearing slides still validate',()=>{
 assert.equal(validPageDesign({widgets:[]}),true);
 assert.equal(validPageDesign({widgets:[{id:'title',kind:'title',label:'Visible'}]}),true);
});
