import test from 'node:test';
import assert from 'node:assert/strict';
import {startsWidgetSelectionOnPointerDown} from '../src/editor-context-input.ts';

test('secondary mouse context press leaves React selection/layout untouched until contextmenu',()=>{
 assert.equal(startsWidgetSelectionOnPointerDown(2),false);
});
test('middle mouse key does not start a drag/selection',()=>{
 assert.equal(startsWidgetSelectionOnPointerDown(1),false);
});
test('primary mouse, touch and pen selection remain enabled',()=>{
 assert.equal(startsWidgetSelectionOnPointerDown(0),true);
});
test('unknown button cannot trigger selection before a contextmenu',()=>{
 assert.equal(startsWidgetSelectionOnPointerDown(-1),false);
});
