import test from 'node:test';
import assert from 'node:assert/strict';
import {pasteWidget} from '../../web/src/widget-clipboard.ts';
test('copy/paste generates a separate identity and preserves editable contents',()=>{
 const w={id:'a',kind:'question',label:'Hello',options:[{id:'opt',label:'Yes'}],position:{x:20,y:10,width:30,height:20}};
 const p=pasteWidget(w,'b');assert.equal(p.id,'b');assert.equal(p.position.x,25);assert.equal(p.options[0].id,'opt');
 p.options[0].label='Changed';assert.equal(w.options[0].label,'Yes');
});
test('paste never places widget beyond slide bounds',()=>{
 const w={id:'a',position:{x:98,y:99,width:40,height:30}};
 const p=pasteWidget(w,'b');assert.equal(p.position.x,60);assert.equal(p.position.y,70);
});
test('paste rejects duplicate identity and normalizes missing position',()=>{
 assert.throws(()=>pasteWidget({id:'a'},'a'));
 const p=pasteWidget({id:'a'},'b');assert.deepEqual(p.position,{x:5,y:5,width:48,height:24});
});
