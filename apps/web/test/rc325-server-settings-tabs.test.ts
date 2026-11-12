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
