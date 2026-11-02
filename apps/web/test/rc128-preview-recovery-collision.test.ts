import test from 'node:test';
import assert from 'node:assert/strict';
import {moveWidgetsToCollisionLimit,overlapsOtherWidgets} from '../src/widget-placement.ts';
import {parseWorkspaceLocation} from '../src/workspace-recovery.ts';
import {answerInputStyle,answerSubmitStyle} from '../src/widget-answer-style.ts';
import {widgetTypographyStyle} from '../src/widget-appearance.ts';

const rect=(id:string,x:number,y:number,width=10,height=10,kind='text')=>({id,kind,position:{x,y,width,height,rotation:0}});
test('RC128: drag stops at the real collision edge rather than teleporting back',()=>{
 const a=rect('dragged',10,10),b=rect('fixed',40,10),original=[a,b];
 const moved=moveWidgetsToCollisionLimit(original,['dragged'],60,0);
 assert.ok(moved[0].position.x>=29.9&&moved[0].position.x<=30.001,JSON.stringify(moved[0]));
 assert.deepEqual(moved[1],b);assert.equal(overlapsOtherWidgets(moved,['dragged']),false);
 assert.equal(original[0].position.x,10);
});
test('RC128: no tunneling through narrow blocker even when final target is empty',()=>{
 const moved=moveWidgetsToCollisionLimit([rect('a',2,2,5,5),rect('b',20,2,2,5)],['a'],70,0);
 assert.ok(moved[0].position.x<=15.01,JSON.stringify(moved[0]));
});
test('RC128: selection stays rigid and graphic overlays may overlap',()=>{
 const source=[rect('a',10,10),rect('b',10,25),rect('blocker',31,10),rect('shape',12,12,8,8,'shape')];
 const moved=moveWidgetsToCollisionLimit(source,['a','b'],50,0);
 assert.ok(moved[0].position.x>=20.9&&moved[0].position.x<=21.001);
 assert.equal(moved[1].position.x,moved[0].position.x);
 assert.equal(overlapsOtherWidgets(moved,['a','b']),false);
 const graphic=moveWidgetsToCollisionLimit(source,['shape'],50,0);
 assert.equal(graphic[3].position.x,62);
});
test('RC128: tab-scoped workspace location accepts only nonsecret typed identifiers',()=>{
 const sid='12345678-1234-4234-8234-123456789abc',pid='12345678-1234-4234-8234-123456789def';
 assert.deepEqual(parseWorkspaceLocation(JSON.stringify({sessionId:sid,section:'session',tab:'pages',pageId:pid,token:'private'})),{sessionId:sid,section:'session',tab:'pages',pageId:pid});
 assert.equal(parseWorkspaceLocation('{bad json').sessionId,'');
 assert.equal(parseWorkspaceLocation(JSON.stringify({sessionId:'https://evil.example',section:'session',pageId:'secret'})).section,'workspace');
 assert.equal(parseWorkspaceLocation(JSON.stringify({sessionId:sid,section:'nonsense',tab:'hack',pageId:pid})).tab,'overview');
});
test('RC128: typography and free-text height retain the same stage coordinate unit',()=>{
 assert.equal(answerInputStyle({answerFieldHeight:192}).height,'15.00000cqw');
 assert.equal(answerSubmitStyle({submitButtonSize:24}).fontSize,'1.87500cqw');
 assert.equal(widgetTypographyStyle({fontFamily:'Georgia',fontSize:24,bold:true}).fontSize,'1.87500cqw');
});
