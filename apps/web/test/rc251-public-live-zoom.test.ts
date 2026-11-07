import test from 'node:test';
import assert from 'node:assert/strict';
import {isUnscaledPublicSurface,zoomStyleValue} from '../src/global-page-zoom.ts';

test('RC251 public participant and presentation screens preserve native pixels',()=>{
 for(const url of ['/join/ABCD12','/join/','/screen/uuid-value','/screen/']){
  assert.equal(isUnscaledPublicSurface(url),true,url);
  for(const setting of [70,80,100,120,150]){
   assert.equal(zoomStyleValue(setting,url),'100%',`${url} at ${setting}%`);
  }
 }
});
test('RC251 studio and master/editor continue using the compact global zoom',()=>{
 for(const url of ['/', '/login','/dashboard','/joiner/abc','/screening/abc']){
  assert.equal(isUnscaledPublicSurface(url),false,url);
  assert.equal(zoomStyleValue(100,url),'80%');
  assert.equal(zoomStyleValue(120,url),'96%');
  assert.equal(zoomStyleValue(150,url),'120%');
 }
 assert.equal(zoomStyleValue(100),'80%');
 assert.equal(isUnscaledPublicSurface(null),false);
 assert.equal(isUnscaledPublicSurface({}),false);
});
