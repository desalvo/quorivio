import test from 'node:test';
import assert from 'node:assert/strict';
import {presenterAdjacentPage,presenterKeyboardDirection,presenterPageIndex} from '../src/presenter-navigation.ts';

const pages=[{id:'slide-a'},{id:'slide-b'},{id:'slide-c'}];
test('presenter opens and resumes the persisted current page, not a local guessed page',()=>{
 assert.equal(presenterPageIndex(pages,'slide-b'),1);
 assert.equal(presenterPageIndex(pages,null),-1);
 assert.equal(presenterPageIndex(pages,'deleted'),-1);
});
test('navigation remains within page boundaries and preserves authored order',()=>{
 assert.equal(presenterAdjacentPage(pages,'slide-b',1)?.id,'slide-c');
 assert.equal(presenterAdjacentPage(pages,'slide-b',-1)?.id,'slide-a');
 assert.equal(presenterAdjacentPage(pages,'slide-a',-1),null);
 assert.equal(presenterAdjacentPage(pages,'slide-c',1),null);
 assert.equal(presenterAdjacentPage(pages,null,1),null);
 assert.deepEqual(pages.map(x=>x.id),['slide-a','slide-b','slide-c']);
});
test('four arrow keys and PageUp/PageDown navigate without modifier keys',()=>{
 for(const key of ['ArrowLeft','ArrowUp','PageUp'])assert.equal(presenterKeyboardDirection({key}),-1);
 for(const key of ['ArrowRight','ArrowDown','PageDown'])assert.equal(presenterKeyboardDirection({key}),1);
 for(const event of [{key:'ArrowRight',altKey:true},{key:'ArrowRight',metaKey:true},{key:'ArrowLeft',ctrlKey:true},{key:' '},{key:'Escape'}])assert.equal(presenterKeyboardDirection(event),null);
});
