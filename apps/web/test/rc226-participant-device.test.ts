import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
import {defaultParticipantPhoneMode} from '../src/participant-device-default.ts';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
test('mobile participant defaults to the phone view while desktop stays 16:9',()=>{
 assert.equal(defaultParticipantPhoneMode(390,true),true);
 assert.equal(defaultParticipantPhoneMode(390,false),true);
 assert.equal(defaultParticipantPhoneMode(844,true),true);
 assert.equal(defaultParticipantPhoneMode(1024,true),false);
 assert.equal(defaultParticipantPhoneMode(1440,false),false);
 assert.equal(defaultParticipantPhoneMode(0,false),false);
 assert.match(ui,/useState\(\(\)=>defaultParticipantPhoneMode\(window\.innerWidth,window\.matchMedia\('\(pointer: coarse\)'\)\.matches\)\)/);
 assert.match(ui,/setParticipantPhoneMode\(true\)/);
 assert.match(ui,/setParticipantPhoneMode\(false\)/);
});
test('master ribbon commands show both icon and caption with accessible descriptions',()=>{
 assert.match(ui,/function SchemaRibbonButton\(/);
 assert.match(ui,/className="slide-scheme-ribbon-icon"/);
 assert.match(ui,/className="slide-scheme-ribbon-caption"/);
 assert.match(ui,/title=\{hint\} aria-label=\{label\+': '\+hint\}/);
 for(const label of ['Titolo','Footer','Sinistra','Destra','In alto','In basso','Salva schema'])assert.ok(ui.includes(label));
});
test('master widget palette uses same IDs/icons and accent categories as page editor',()=>{
 assert.match(ui,/className="slide-scheme-widget-options"/);
 assert.match(ui,/<EditorWidgetIcon kind=\{kind\}\/>/);
 assert.match(ui,/data-widget-kind=\{kind\}/);
 assert.match(css,/\.slide-scheme-widget-options>button\[data-widget-kind\]/);
 assert.match(css,/\.slide-scheme-widget-options>\[data-widget-kind=question\]/);
});
test('mobile-only presenter workspace and page editor layout retain desktop separation',()=>{
 assert.match(css,/RC226 — Mobile presenter\/admin workspace/);
 assert.match(css,/@media\(max-width:760px\)\{/);
 assert.match(css,/body \.editor-ux-v2 \.page-editor-thumbnails\{display:flex!important;flex-direction:row!important/);
 assert.match(css,/body \.editor-ux-v2 \.editor-stage\{/);
});
