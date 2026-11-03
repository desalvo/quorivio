import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {validWidgetTextStyle} from '../../api/src/domain.ts';

test('RC142: independent footer format and rating size have bounded validation',()=>{
 assert.equal(validWidgetTextStyle({ratingButtonSize:32,footerNumberFontFamily:'Georgia',footerNumberFontSize:16,footerNumberColor:'#1188aa',footerNumberPaddingRight:5,footerNumberPaddingBottom:5}),true);
 assert.equal(validWidgetTextStyle({ratingButtonSize:1000}),false);
 assert.equal(validWidgetTextStyle({footerNumberPaddingBottom:-1}),false);
 assert.equal(validWidgetTextStyle({footerNumberColor:'javascript:bad'}),false);
});
test('RC142: palette, vertical alignment, shortcut keys and phone preview retain actual controls',()=>{
 const s=fs.readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 for(const x of ['readEditorWidgetClipboard(sessionId)','event.key===\'Backspace\'','Allinea testo in basso','Dimensione pulsanti gradimento','Padding inferiore numero pagina','Anteprima smartphone','Dispositivo partecipante'])assert.ok(s.includes(x),x);
 const css=fs.readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
 assert.ok(css.includes('.rehearsal-phone-frame'));
 assert.ok(css.includes('grid-template-rows:29px'));
});
