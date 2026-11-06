import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
import {defaultParticipantPhoneMode} from '../src/participant-device-default.ts';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
test('background gallery is a single icon-labelled ribbon command, not embedded thumbnails',()=>{
 assert.match(ui,/function SchemaBackgroundTool\(/);
 assert.match(ui,/<SchemaRibbonButton label="Sfondi" hint="Apri la libreria di sfondi/);
 assert.match(ui,/<SchemaBackgroundTool items=\{assets\.filter/);
 const ribbon=ui.slice(ui.indexOf('<div className="slide-scheme-ribbon"'),ui.indexOf('<div className="slide-scheme-widget-rail"'));
 assert.doesNotMatch(ribbon,/<BackgroundGallery\b/);
 assert.match(ui,/className="schema-background-modal" role="dialog" aria-modal="true"/);
 assert.match(ui,/onMouseDown=\{e=>\{if\(e\.target===e\.currentTarget\)setOpen\(false\)\}\}/);
});
test('modal has keyboard handling, labelled title, focus restoration and thumbnail selection',()=>{
 const tool=ui.slice(ui.indexOf('function SchemaBackgroundTool('),ui.indexOf('function App(){'));
 for(const value of ['dialogRef.current?.focus()',"event.key==='Escape'","event.key!=='Tab'",'document.addEventListener(\'keydown\',onKey,true)','previous?.focus()', 'aria-labelledby="schema-background-modal-title"', 'aria-describedby="schema-background-modal-description"','onSelect={id=>{onSelect(id);setOpen(false)}}']) assert.ok(tool.includes(value),value);
});
test('automatic participant phone layout updates with rotation but never overrides a manual choice',()=>{
 assert.equal(defaultParticipantPhoneMode(390,true),true);
 assert.equal(defaultParticipantPhoneMode(844,true),true);
 assert.equal(defaultParticipantPhoneMode(1100,true),false);
 const start=ui.indexOf('const [participantModeExplicit,setParticipantModeExplicit]=useState(false)');
 const end=ui.indexOf('const [myProfile',start);
 assert.ok(start>=0&&end>start);
 const effect=ui.slice(start,end);
 for(const text of ['if(participantModeExplicit)return;',"window.addEventListener('resize',sync)","pointer.addEventListener('change',sync)","window.removeEventListener('resize',sync)","pointer.removeEventListener('change',sync)",'defaultParticipantPhoneMode(window.innerWidth,pointer.matches)']) assert.ok(effect.includes(text),text);
 for(const label of ['Diapositiva 16:9','Layout smartphone','Lettura accessibile']){
  const point=ui.indexOf('>'+label+'</button>');assert.ok(point>0,label);
  assert.ok(ui.slice(Math.max(0,point-240),point).includes('setParticipantModeExplicit(true)'),label);
 }
});
test('gallery modal remains constrained to viewport and remains scrollable on phones',()=>{
 assert.match(css,/\.schema-background-modal-backdrop\{position:fixed;z-index:/);
 assert.match(css,/\.schema-background-modal\{[^\n]*max-height:calc\(100dvh - 24px\)/);
 assert.match(css,/\.schema-background-modal \.background-gallery\{[^\n]*overflow-y:auto/);
 assert.match(css,/@media\(max-width:440px\)\{\.schema-background-modal\{/);
});
