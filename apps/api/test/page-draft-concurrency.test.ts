import test from 'node:test';
import assert from 'node:assert/strict';
import {pageDraftFromActivity,pageDraftSignature,validDesignRevision} from '../../web/src/page-draft.ts';

const initial={page_design:{widgets:[{id:'first',kind:'text',label:'hello'}],header:'Q',backgroundUrl:'https://example.org/a',backgroundColor:'#AABBCC',backgroundAssetId:'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'},result_design:{header:'R',backgroundUrl:'https://example.org/b',backgroundColor:'#112233',backgroundAssetId:'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'}};
test('loaded draft signature equals a freshly serialized editor draft',()=>{
 const d=pageDraftFromActivity(initial);assert.equal(pageDraftSignature(d),pageDraftSignature({...d}));
});
test('question background color changes mark the page dirty',()=>{
 const d=pageDraftFromActivity(initial);assert.notEqual(pageDraftSignature(d),pageDraftSignature({...d,questionBackgroundColor:'#FFFFFF'}));
});
test('result background color changes mark the page dirty',()=>{
 const d=pageDraftFromActivity(initial);assert.notEqual(pageDraftSignature(d),pageDraftSignature({...d,resultBackgroundColor:'#FFFFFF'}));
});
test('question background asset changes mark the page dirty',()=>{
 const d=pageDraftFromActivity(initial);assert.notEqual(pageDraftSignature(d),pageDraftSignature({...d,questionBackgroundAsset:''}));
});
test('result background asset changes mark the page dirty',()=>{
 const d=pageDraftFromActivity(initial);assert.notEqual(pageDraftSignature(d),pageDraftSignature({...d,resultBackgroundAsset:''}));
});
test('question heading changes mark the page dirty',()=>{
 const d=pageDraftFromActivity(initial);assert.notEqual(pageDraftSignature(d),pageDraftSignature({...d,questionHeader:'Different'}));
});
test('result heading changes mark the page dirty',()=>{
 const d=pageDraftFromActivity(initial);assert.notEqual(pageDraftSignature(d),pageDraftSignature({...d,resultHeader:'Different'}));
});
test('widget edits mark the page dirty without mutating the loaded activity',()=>{
 const d=pageDraftFromActivity(initial);const next={...d,widgets:[{...d.widgets[0] as object,label:'changed'}]};assert.notEqual(pageDraftSignature(d),pageDraftSignature(next));assert.equal((initial.page_design.widgets[0] as any).label,'hello');
});
test('missing page and result design fields normalize to empty defaults',()=>{
 const d=pageDraftFromActivity({});assert.deepEqual(d,{widgets:[],questionHeader:'',resultHeader:'',questionBackground:'',resultBackground:'',questionBackgroundColor:'',resultBackgroundColor:'',questionBackgroundAsset:'',resultBackgroundAsset:''});
});
test('undefined fields normalize to same signature as empty strings',()=>{
 const a=pageDraftFromActivity({page_design:{header:undefined,backgroundColor:undefined},result_design:{backgroundAssetId:undefined}});
 assert.equal(pageDraftSignature(a),pageDraftSignature(pageDraftFromActivity({})));
});
test('valid design revision accepts positive safe integers only',()=>{
 for(const x of [1,2,999,Number.MAX_SAFE_INTEGER])assert.equal(validDesignRevision(x),true);
 for(const x of [0,-1,1.2,NaN,Infinity,-Infinity,'1',true,null,undefined,{},[],Number.MAX_SAFE_INTEGER+1])assert.equal(validDesignRevision(x),false,String(x));
});
test('separate drafts with identical content have stable signatures',()=>{
 const a=pageDraftFromActivity(initial),b=pageDraftFromActivity(JSON.parse(JSON.stringify(initial)));
 assert.equal(pageDraftSignature(a),pageDraftSignature(b));
});
