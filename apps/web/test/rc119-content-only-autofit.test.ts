import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {autoFitExpandedPosition,measuredContentOverflowPx} from '../src/widget-auto-fit.ts';
import {insertWidgetGroupInFreeSpace} from '../src/widget-selection.ts';
const editor=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const browser=readFileSync(new URL('../../../tools/ci_browser_editor.py',import.meta.url),'utf8');
const original=[
 {id:'widget-a',kind:'text',position:{x:10,y:10,width:20,height:20}},
 {id:'widget-b',kind:'text',position:{x:40,y:35,width:15,height:15}},
 {id:'widget-c',kind:'text',position:{x:75,y:70,width:15,height:10}}
];
test('protruding 6px handles are not text overflow',()=>{
 assert.equal(measuredContentOverflowPx(92,92),0);
 assert.equal(measuredContentOverflowPx(92,94),2);
 assert.equal(autoFitExpandedPosition(original[0].position,measuredContentOverflowPx(92,92),460),null);
 assert.match(editor,/proportionalWidgetScale\(\{/);
 assert.match(editor,/const next=proportionalWidgetScale/);
 assert.doesNotMatch(editor,/const overflow=node\.scrollHeight-node\.clientHeight/);
});
test('genuine oversized content grows once and then stops',()=>{
 const initial=original[0].position;
 const overflow=measuredContentOverflowPx(92,135);
 const next=autoFitExpandedPosition(initial,overflow,460);
 assert.ok(next && next.height>initial.height);
 assert.equal(measuredContentOverflowPx(145,135),0);
 assert.equal(autoFitExpandedPosition(next!,0,460),null);
 assert.equal(measuredContentOverflowPx(Number.NaN,135),0);
});
test('original browser short-text fixture can duplicate two widgets without collisions',()=>{
 const result=insertWidgetGroupInFreeSpace(original,original.slice(0,2),['copy-a','copy-b']);
 assert.ok(result,'short text widgets must leave valid group placement');
 assert.equal(result!.widgets.length,5);
 assert.deepEqual(result!.selected,['copy-a','copy-b']);
 assert.match(browser,/fixture_geometry=await page\.locator/);
 assert.match(browser,/all\(g\['height'\]<26 for g in fixture_geometry\)/);
 assert.match(browser,/assert not duplication_alerts, \('Group duplication rejected:/);
 assert.match(browser,/to_have_count\(5\)/);
 assert.match(browser,/to_have_count\(3\)/);
});
