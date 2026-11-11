import test from 'node:test';
import assert from 'node:assert/strict';
import {presenterKeyboardDirection} from '../src/presenter-navigation.ts';
import {rehearsalPageDirection} from '../src/rehearsal-navigation.ts';
import {blocksSlideNavigation} from '../src/slide-keyboard-guard.ts';

const inAncestor=(kind:string):EventTarget=>({
 closest:(selector:string)=>selector.split(',').includes(kind)?{}:null
}) as unknown as EventTarget;

test('RC303 the stage still navigates with unmodified arrows and Page keys',()=>{
 for(const [key,expected] of [['ArrowLeft',-1],['ArrowRight',1],['ArrowUp',-1],['ArrowDown',1],['PageUp',-1],['PageDown',1]] as const)
  assert.equal(presenterKeyboardDirection({key}),expected);
 for(const [key,expected] of [['ArrowLeft',-1],['ArrowRight',1],['PageUp',-1],['PageDown',1]] as const)
  assert.equal(rehearsalPageDirection({key}),expected);
 assert.equal(rehearsalPageDirection({key:'ArrowDown'}),0);
 assert.equal(presenterKeyboardDirection({key:'Escape'}),null);
});

test('RC303 controls, nested dialogs, rich-text editors and media own Arrow/Page keys',()=>{
 const controls=[
  'input','textarea','select','button','a','summary','iframe','audio','video',
  '[contenteditable]','[role="textbox"]','[role="slider"]',
  '[role="spinbutton"]','[role="combobox"]','[role="listbox"]',
  '[role="option"]','[role="radio"]','[role="radiogroup"]',
  '[role="checkbox"]','[role="switch"]','[role="menu"]',
  '[role="menuitem"]','[role="menuitemcheckbox"]','[role="menuitemradio"]',
  '[role="tab"]','[role="tablist"]','[role="button"]','[role="link"]',
  '[role="tree"]','[role="treeitem"]','[role="grid"]','[role="gridcell"]',
  '[role="dialog"]','[aria-modal="true"]','[data-no-slide-keyboard]'
 ];
 for(const kind of controls){
  for(const key of ['ArrowLeft','ArrowRight','PageUp','PageDown']){
   const event={key,target:inAncestor(kind)};
   assert.equal(presenterKeyboardDirection(event),null,'presenter leaked '+key+' at '+kind);
   assert.equal(rehearsalPageDirection(event),0,'rehearsal leaked '+key+' at '+kind);
  }
 }
});

test('RC303 modified, consumed, composing and repeated events cannot cause slide bursts',()=>{
 for(const flag of ['shiftKey','altKey','ctrlKey','metaKey','defaultPrevented','isComposing','repeat'] as const){
  const event={key:'ArrowRight',[flag]:true};
  assert.equal(blocksSlideNavigation(event),true,flag);
  assert.equal(presenterKeyboardDirection(event),null,flag);
  assert.equal(rehearsalPageDirection(event),0,flag);
 }
});

test('RC303 non-Element targets and non-interactive canvas stay valid',()=>{
 for(const target of [undefined,null,{} as EventTarget,inAncestor('canvas'),inAncestor('[role="region"]')]){
  assert.equal(presenterKeyboardDirection({key:'PageDown',target}),1);
  assert.equal(rehearsalPageDirection({key:'PageDown',target}),1);
 }
});
