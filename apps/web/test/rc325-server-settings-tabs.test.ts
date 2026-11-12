import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const locale=readFileSync(new URL('../src/ui-locale.ts',import.meta.url),'utf8');
test('server settings renders seven keyboard-accessible tabs with matching panels',()=>{
 const tabs=['general','auth','smtp','storage','converter','backup','audit'];
 for(const name of tabs){
  assert.match(main,new RegExp('id="server-settings-panel-'+name+'"'));
  assert.match(main,new RegExp("hidden=\\{serverSettingsTab!=='"+name+"'\\}"));
  assert.match(main,new RegExp("\\{id:'"+name+"'"));
 }
 assert.match(main,/role="tablist"/);
 assert.match(main,/role="tab"/);
 assert.match(main,/aria-controls=\{'server-settings-panel-'\+item\.id\}/);
 assert.match(main,/aria-selected=\{serverSettingsTab===item\.id\}/);
 assert.match(main,/ArrowLeft/);
 assert.match(main,/ArrowRight/);
 assert.match(main,/Home/);
 assert.match(main,/End/);
 assert.match(css,/\[role="tabpanel"\]\[hidden\]\{display:none!important\}/);
});
test('inactive auth forms stay mounted while changing server tabs',()=>{
 const section=main.slice(main.indexOf('<AuthBackendSettingsPanel request={request}/>')-140,main.indexOf('<AuthBackendSettingsPanel request={request}/>')+250);
 assert.match(section,/hidden=\{serverSettingsTab!=='auth'\}/);
 assert.match(main,/<AdminBackupPanel\/>/);
 assert.match(main,/<AdminAuditPanel\/>/);
 assert.doesNotMatch(main,/serverSettingsTab==='auth'&&<AuthBackendSettingsPanel/);
});
test('language switch updates UI copy, menu labels, document language and accessibility attributes',()=>{
 assert.match(main,/preferredUiLanguage/);
 assert.match(main,/activateUiLanguage\(lang\)/);
 assert.match(main,/translateUiText\(label,lang\)/);
 assert.match(main,/translateUiText\(item\.label,lang\)/);
 assert.match(locale,/document\.documentElement\.lang=language/);
 assert.match(locale,/MutationObserver/);
 assert.match(locale,/aria-label','title','placeholder/);
 assert.match(locale,/contenteditable/);
});

test('RC329 server tabs always have visible controls and WCAG-AA text contrast',()=>{
 const fix=css.split('/* RC329: platform server tabs live inside a dark dashboard.')[1]||'';
 assert.ok(fix,'missing RC329 scoped tab contrast override');
 assert.match(fix,/\.dashboard \.server-settings-tabs > button\.server-settings-tab\{/);
 assert.match(fix,/visibility:visible!important;opacity:1!important/);
 assert.match(fix,/min-height:44px!important/);
 assert.match(fix,/white-space:nowrap!important/);
 assert.match(fix,/\.server-settings-tab\[aria-selected="true"\]/);
 assert.match(fix,/\.server-settings-tab:focus-visible/);
 const brightness=(hex:string)=>{
  const rgb=hex.match(/[a-f\d]{2}/gi);
  assert.ok(rgb&&rgb.length===3,'valid RGB colour '+hex);
  const values=rgb.map(x=>parseInt(x,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);
  return .2126*values[0]+.7152*values[1]+.0722*values[2];
 };
 const contrast=(a:string,b:string)=>{
  const hi=Math.max(brightness(a),brightness(b)),lo=Math.min(brightness(a),brightness(b));
  return (hi+.05)/(lo+.05);
 };
 for(const [name,textColor,background] of [
  ['inactive','#f8fbff','#26465f'],
  ['hover','#ffffff','#345d7d'],
  ['selected','#ffffff','#096858'],
 ]){
  assert.ok(fix.includes('background:'+background+'!important'),name+' background must be explicit');
  assert.ok(fix.includes('color:'+textColor+'!important'),name+' text must be explicit');
  assert.ok(contrast(textColor,background)>=4.5,name+' must pass WCAG AA');
 }
 assert.match(fix,/@media\(max-width:640px\)\{[\s\S]*?overflow-x:auto!important/);
 assert.match(fix,/scrollbar-width:thin!important/);
 assert.match(main,/role="tablist"/);
 assert.match(main,/tabIndex=\{serverSettingsTab===item\.id\?0:-1\}/);
});
test('RC331 server tabs do not animate into an inaccessible selected colour',()=>{
 const block=css.split('/* RC329: platform server tabs live inside a dark dashboard.')[1]||'';
 assert.match(block,/\.dashboard \.server-settings-tabs > button\.server-settings-tab\{[\s\S]*?transition:none!important/);
 const chromium=readFileSync(new URL('../../../tools/ci_rc329_server_settings_tabs_chromium.py',import.meta.url),'utf8');
 assert.match(chromium,/metric\["transitionDuration"\] == "0s"/);
});
