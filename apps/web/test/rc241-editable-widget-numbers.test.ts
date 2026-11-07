import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parsedEditableNumber,stepEditableNumber} from '../src/editable-number-value.ts';
const input=readFileSync(new URL('../src/editable-number-field.tsx',import.meta.url),'utf8');
const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const format=readFileSync(new URL('../src/result-format-controls.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('empty, partial, and out of bounds are preserved as drafts instead of coercing to zero',()=>{
 assert.equal(parsedEditableNumber('',10,96),null);
 assert.equal(parsedEditableNumber(' ',10,96),null);
 assert.equal(parsedEditableNumber('2',10,96),null);
 assert.equal(parsedEditableNumber('24',10,96),24);
 assert.equal(parsedEditableNumber('97',10,96),null);
 assert.equal(parsedEditableNumber('12,5',0,30),12.5);
 assert.equal(parsedEditableNumber('Infinity',0,96),null);
});
test('keyboard and explicit arrows respect step, decimals, minimum and maximum',()=>{
 assert.equal(stepEditableNumber('16',16,10,96,1,1),17);
 assert.equal(stepEditableNumber('10',10,10,96,1,-1),10);
 assert.equal(stepEditableNumber('96',96,10,96,1,1),96);
 assert.equal(stepEditableNumber('',16,10,96,1,1),17);
 assert.equal(stepEditableNumber('1.25',1.25,0,12,0.25,1),1.5);
 assert.equal(stepEditableNumber('11.75',11.75,0,12,0.5,1),12);
});
test('every format numeric control supports raw typing, Enter/blur commit and two accessible arrows',()=>{
 assert.match(input,/onChange=\{e=>\{const next=e\.currentTarget\.value;setDraft\(next\)/);
 assert.match(input,/onBlur=\{e=>\{focused\.current=false;commit\(e\.currentTarget\.value\)\}\}/);
 assert.match(input,/e\.key==='Enter'/);
 assert.match(input,/e\.key==='ArrowUp'/);
 assert.match(input,/aria-label=\{'Aumenta '\+ariaLabel/);
 assert.match(input,/aria-label=\{'Diminuisci '\+ariaLabel/);
 assert.match(css,/\.widget-selection-palette \.editable-number-arrows>button/);
 for(const label of ['Spessore bordo widget','Larghezza risposta libera','Altezza risposta libera','Padding destro numero pagina','Padding inferiore numero pagina','Dimensione emoji reazioni','Dimensione pulsanti gradimento']){
  assert.ok(main.includes('<EditableNumberField ariaLabel="'+label+'"'),label);
 }
 assert.match(main,/title="Aumenta di 1" onMouseDown=\{e=>e\.preventDefault\(\)\}/);
 assert.match(main,/title="Diminuisci di 1" onMouseDown=\{e=>e\.preventDefault\(\)\}/);
 assert.match(format,/EditableNumberField ariaLabel=\{'Dimensione '\+item\.label\}/);
 assert.ok(!format.includes('<input type="number"'));
});
test('per-option font-size edits retain the unique source question/answer key',()=>{
 assert.match(format,/key=\{item\.key\}/);
 assert.match(format,/onCommit=\{n=>update\(item\.key,\{fontSize:n\}\)\}/);
 assert.match(format,/resultElementKey\('row',questionId,o\.id\)/);
 assert.match(main,/data-result-custom=\{widget\.resultTextStyles\?\.\[resultElementKey\('row'/);
});
