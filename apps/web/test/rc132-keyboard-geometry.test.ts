import test from 'node:test';
import assert from 'node:assert/strict';
import {nudgeWidgetSelection} from '../src/widget-selection.ts';
import {moveWidgetsToCollisionLimit,overlapsOtherWidgets} from '../src/widget-placement.ts';
import {answerFieldHeightForKey,answerFieldHeight,MIN_ANSWER_FIELD_HEIGHT,MAX_ANSWER_FIELD_HEIGHT} from '../src/answer-field-resize.ts';
import {beginWidgetGesture,editWidgets,endWidgetGesture,newWidgetHistory,undoWidgets} from '../src/widget-history.ts';

const w=(id:string,x:number,y:number,width=10,height=10,kind='question')=>({id,kind,position:{x,y,width,height,rotation:0},style:{answerFieldHeight:96}});

test('RC138 keyboard nudge can travel through another widget',()=>{
 const base=[w('moving',2,10,5,10),w('thin',30.05,10,.05,10)];
 const moved=nudgeWidgetSelection(base,['moving'],90,0);
 assert.equal(moved[0].position.x,92);assert.equal(base[0].position.x,2);
});
test('RC138 keyboard group nudge preserves offsets and respects canvas bounds',()=>{
 const base=[w('a',5,10),w('b',5,35),w('wall',35,10,5,10)];
 const moved=nudgeWidgetSelection(base,['a','b'],90,0);
 assert.equal(moved[0].position.x,90);assert.equal(moved[1].position.x,90);
 assert.equal(moved[1].position.y-moved[0].position.y,25);
});
test('RC132 keyboard nudge honors graphic overlays and canvas bounds',()=>{
 const base=[w('shape',8,10,10,10,'shape'),w('block',25,10,5,10)];
 assert.equal(nudgeWidgetSelection(base,['shape'],90,0)[0].position.x,90);
 assert.equal(nudgeWidgetSelection([w('m',90,90,10,10)],['m'],20,0)[0].position.x,90);
});
test('RC132 a missing selection and invalid motion are strict no-ops',()=>{
 const base=[w('a',10,10)];
 assert.equal(nudgeWidgetSelection(base,['other'],2,0),base);
 assert.equal(nudgeWidgetSelection(base,['a'],Infinity,0),base);
});
test('RC132 group keyboard nudge remains one undoable edit',()=>{
 const base=[w('a',5,10),w('b',5,35),w('wall',35,10,5,10)];
 let history=newWidgetHistory(base);
 history=editWidgets(history,nudgeWidgetSelection(history.present,['a','b'],70,0));
 history=undoWidgets(history);
 assert.deepEqual(history.present,base);
});
test('RC132 keyboard response resize has bounded single and accelerated steps',()=>{
 assert.equal(answerFieldHeightForKey(96,'ArrowDown'),104);
 assert.equal(answerFieldHeightForKey(96,'ArrowUp'),88);
 assert.equal(answerFieldHeightForKey(96,'ArrowDown',true),128);
 assert.equal(answerFieldHeightForKey(96,'PageDown'),128);
 assert.equal(answerFieldHeightForKey(96,'PageUp'),64);
});
test('RC132 keyboard response resize supports start/end and strict bounds',()=>{
 assert.equal(answerFieldHeightForKey(96,'Home'),MIN_ANSWER_FIELD_HEIGHT);
 assert.equal(answerFieldHeightForKey(96,'End'),MAX_ANSWER_FIELD_HEIGHT);
 assert.equal(answerFieldHeightForKey(398,'ArrowDown'),400);
 assert.equal(answerFieldHeightForKey(50,'ArrowUp'),48);
 assert.equal(answerFieldHeightForKey(96,'Space'),null);
 assert.equal(answerFieldHeightForKey(96,'ArrowLeft'),null);
});
test('RC132 corrupted response height cannot propagate to editor geometry',()=>{
 assert.equal(answerFieldHeight(NaN),96);
 assert.equal(answerFieldHeight(Infinity),96);
 assert.equal(answerFieldHeight(0),96);
 assert.equal(answerFieldHeight(48.5),96);
 assert.equal(answerFieldHeight(192),192);
 assert.equal(answerFieldHeightForKey(NaN,'ArrowDown'),104);
});
test('RC132 keyboard response resize commits one history entry and is reversible',()=>{
 const base=[w('question',10,10)];
 let history=newWidgetHistory(base);
 history=beginWidgetGesture(history);
 const height=answerFieldHeightForKey(96,'ArrowDown')!;
 history=editWidgets(history,[{...base[0],style:{answerFieldHeight:height}}]);
 history=endWidgetGesture(history);
 assert.equal(history.past.length,1);
 assert.equal(undoWidgets(history).present[0].style.answerFieldHeight,96);
});
test('RC132 nudge is semantically the same continuous bounded movement as pointer',()=>{
 const base=[w('a',10,15,8,8),w('wall',31,30,5,5)];
 assert.deepEqual(nudgeWidgetSelection(base,['a'],50,50),moveWidgetsToCollisionLimit(base,['a'],50,50));
});
