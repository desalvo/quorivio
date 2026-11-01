import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveSlideMasterWidgets,masterWidgetTemplate,normalizeLegacyFooter} from '../src/master-widget-utils.ts';

test('global scheme populates missing Title and Footer without mutating the page',()=>{
 const page=[{id:'text-1',kind:'text',label:'Own text'}];
 const master=[{id:'schema-title',kind:'title',label:'Master'}, {id:'schema-footer',kind:'footer',label:''}];
 const merged=resolveSlideMasterWidgets(page,master);
 assert.deepEqual(merged.map(w=>w.kind),['title','footer','text']);
 assert.deepEqual(page,[{id:'text-1',kind:'text',label:'Own text'}]);
 assert.ok(merged[0].id.startsWith('inherited-'));
});
test('local page Title and Footer override only matching scheme kinds',()=>{
 const master=[{id:'t',kind:'title',label:'Template'}, {id:'f',kind:'footer',label:'Footer'}];
 const page=[{id:'own-title',kind:'title',label:'Own'}];
 assert.deepEqual(resolveSlideMasterWidgets(page,master).map(w=>w.kind),['footer','title']);
 assert.deepEqual(resolveSlideMasterWidgets(page,[...master]),resolveSlideMasterWidgets(page,master));
});
test('scheme editor keeps generic widgets but at most one Title and Footer',()=>{
 const all=[{id:'t',kind:'title'},{id:'f',kind:'footer'},{id:'t2',kind:'title'},{id:'other',kind:'quiz'}];
 assert.deepEqual(masterWidgetTemplate(all).map(w=>w.id),['t','f','other']);
});

test('an old unmodified default footer is moved back inside the stage; custom layout is untouched',()=>{
 const old={id:'old',kind:'footer',position:{x:0,y:94,width:100,height:6,rotation:0}};
 assert.deepEqual(normalizeLegacyFooter(old).position,{x:0,y:87,width:100,height:13,rotation:0});
 assert.equal(old.position.y,94);
 assert.equal(normalizeLegacyFooter({...old,position:{...old.position,x:5}}).position.x,5);
});

test('a linked result in the master inherits its linked source ID correctly',()=>{
 const master=[{id:'source',kind:'question',label:'Q'}, {id:'results',kind:'results-button',targetWidgetId:'source'}];
 const merged=resolveSlideMasterWidgets([{id:'own',kind:'text'}],master);
 assert.equal((merged[1] as any).targetWidgetId,merged[0].id);
 assert.equal(merged[0].id,'inherited-source');
});
