import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {resolveSlideMasterWidgets} from '../src/master-widget-utils.ts';
import {footerPageNumber,newFooterWidget} from '../src/slide-master.ts';

const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');

test('RC170 the editor renders a master-owned page number without copying the master into the local draft',()=>{
 const master={...newFooterWidget('master-footer'),style:{fontFamily:'Arial',fontSize:19,footerNumberFontSize:22,footerNumberPaddingRight:17,footerNumberPaddingBottom:13}};
 const local=[{id:'question-one',kind:'question'}];
 const projected=resolveSlideMasterWidgets(local,[master]);
 assert.equal(local.length,1);
 assert.equal(projected.length,2);
 assert.equal(projected[0].id,'inherited-master-footer');
 const number=footerPageNumber(projected,7);
 assert.equal(number?.fontSize,22);
 assert.equal(number?.paddingRight,17);
 assert.equal(number?.paddingBottom,13);
 assert.ok(main.includes('numberingWidgets={resolveSlideMasterWidgets(pageWidgets,snap.session.theme?.master?.widgets)}'));
 assert.ok(main.includes('<SlideCanvasNumber widgets={numberingWidgets??widgets} pageNumber={pageNumber}/>'));
});

test('RC170 page footer overrides master; no accidental extra page number',()=>{
 const master=newFooterWidget('master-footer');
 const hidden={...newFooterWidget('local-footer'),footerShowPageNumber:false};
 const result=resolveSlideMasterWidgets([hidden],[master]);
 assert.equal(result.filter(w=>w.kind==='footer').length,1);
 assert.equal(footerPageNumber(result,3),null);
});

test('RC170 phone renderers use authored logical pixels while desktop keeps cqw',()=>{
 for(const item of ['--phone-footer-number-font-size','--phone-footer-pad-right','--phone-footer-pad-bottom']){
  assert.ok(main.includes(`'${item}'`));
  assert.ok(css.includes(`var(${item},`));
 }
 const gate=css.split('/* RC170: footer number follows one logical phone specification')[1];
 assert.ok(gate);
 for(const selector of ['.rehearsal-phone-stage','.audience-widget-layout.stage-phone','.canvas-editor-group[data-canvas-device="phone"]']){
  assert.ok(gate.includes(selector),selector);
 }
 assert.match(gate,/\.slide-canvas-page-number\[data-custom-number="true"\]/);
 assert.match(gate,/right:auto!important/);
});
