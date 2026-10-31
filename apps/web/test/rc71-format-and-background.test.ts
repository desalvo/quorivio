import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
test('cloud entries display counts in square brackets across all presentations',()=>{
 assert.match(src,/<small> \[\{count\}\]<\/small>/);
 assert.match(src,/chart==='cloud'\?`\[\$\{r\.count\}\]`/);
 assert.match(src,/\{w\.word\} \[\{w\.count\}\]/);
});
test('background file input outlives contextual menu unmount and routes uploaded image to library',()=>{
 assert.match(src,/backgroundFileRef=useRef<HTMLInputElement>/);
 assert.match(src,/ref=\{backgroundFileRef\}/);
 assert.match(src,/void onBackgroundUpload\(file\)/);
 assert.match(src,/setBackgroundMenu\(false\)/);
 assert.match(src,/await refreshAssets\(\);setNotice\('Immagine caricata nella libreria/);
 assert.match(src,/setQuestionBackgroundAsset\(applied\.id\)/);
});
test('presenter custom text, reaction icon size, and enlarged artistic palette are configurable',()=>{
 assert.match(src,/Testo opzionale profilo presentatore/);
 assert.match(src,/Dimensione icone reazioni/);
 assert.match(src,/presenter-profile-custom-text/);
 assert.match(src,/--reaction-size/);
 assert.match(css,/\.widget-selection-palette\{gap:9px!important/);
 assert.match(css,/\.widget-reactions-live button\{font-size:var\(--reaction-size/);
});
