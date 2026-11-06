import test from 'node:test';
import assert from 'node:assert/strict';
import {choosePageIds,orderedSelectedPageIds,duplicatePageOrder,thumbnailShortcut} from '../src/page-thumbnail-selection.ts';
import {slidePageNumber} from '../src/slide-master.ts';

test('Ctrl/Cmd click adds or removes thumbnails without losing ordinary single selection',()=>{
 assert.deepEqual(choosePageIds(['a'],'b',true),['a','b']);
 assert.deepEqual(choosePageIds(['a','b'],'a',true),['b']);
 assert.deepEqual(choosePageIds(['a','b'],'c',false),['c']);
});
test('operations preserve persisted page order, not click order',()=>{
 assert.deepEqual(orderedSelectedPageIds([{id:'a'},{id:'b'},{id:'c'}],['c','a']),['a','c']);
 assert.deepEqual(duplicatePageOrder(['a','b','c'],new Map([['a','a2'],['c','c2']])),['a','a2','b','c','c2']);
});
test('D,R,Backspace are scoped to thumbnail focus and do not hijack typing',()=>{
 assert.equal(thumbnailShortcut({key:'d'},true),'duplicate');
 assert.equal(thumbnailShortcut({key:'R'},true),'rename');
 assert.equal(thumbnailShortcut({key:'Backspace'},true),'delete');
 assert.equal(thumbnailShortcut({key:'d'},false),null);
 assert.equal(thumbnailShortcut({key:'d',ctrlKey:true},true),null);
 assert.equal(thumbnailShortcut({key:'Backspace',repeat:true},true),null);
});
test('presenter numbers exclude hidden pages; independent audience page shares presenter ordinal',()=>{
 const activities=[{id:'hidden',page_design:{presenterHidden:true}},{id:'p2',page_design:{}},{id:'private',page_design:{presenterHidden:true}},{id:'p4',page_design:{}}];
 assert.equal(slidePageNumber(activities,'p2'),1);
 assert.equal(slidePageNumber(activities,'p4'),2);
 assert.equal(slidePageNumber(activities,'private'),1);
 assert.equal(slidePageNumber(activities,'missing'),0);
});
