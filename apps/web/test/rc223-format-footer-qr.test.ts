import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {test} from 'node:test';
const root=path.resolve(import.meta.dirname,'../../..');
const ui=readFileSync(path.join(root,'apps/web/src/main.tsx'),'utf8');
const css=readFileSync(path.join(root,'apps/web/src/style.css'),'utf8');

test('format opens only from the selected widget context menu',()=>{
 assert.match(ui,/const \[ribbonDismissed,setRibbonDismissed\]=useState\(true\)/);
 assert.match(ui,/const toggleSelection=.*?setRibbonDismissed\(true\)/);
 assert.match(ui,/aria-label="Formato widget" onClick=\{\(\)=>\{setActive\(w.id\)/);
 assert.match(ui,/setFormatTab\('text'\);setRibbonDismissed\(false\);setContextWidget\(null\)/);
});
test('format tabs expose existing server-validated borders effects visibility and linked results',()=>{
 for(const entry of ['"widget-format-tabs" role="tablist"',"'border'",'aria-label="Spessore bordo widget"','aria-label="Effetto grafico widget"','aria-label="Pagina collegata ai risultati"','Mostra testo della domanda'])
  assert.ok(ui.includes(entry),entry);
});
test('footer authored horizontal and vertical alignment overrides old forced centering',()=>{
 assert.match(css,/RC223: footer uses the authored paragraph/);
 assert.match(css,/flex:0 0 auto!important;text-align:inherit!important/);
 assert.match(css,/data-vertical-align="bottom"\] \.projection-slide-footer\{justify-content:flex-end!important/);
});
test('QR link is one line and scrolls instead of scaling whole QR widget',()=>{
 assert.match(ui,/className="participant-qr-url" href=\{url\} title=\{url\}/);
 assert.match(css,/min-height:22px!important;height:auto!important;max-height:24px!important/);
 assert.match(css,/white-space:nowrap!important;word-break:normal!important/);
 assert.ok(ui.includes("allowScale={!['qr','participant-count'].includes(w.kind)"));
});
test('participant count sizes from widget box and hides title without losing count',()=>{
 assert.match(css,/\.projection-participant-count\{[\s\S]*?container-type:size/);
 assert.match(css,/\[data-show-title="false"\] \.projection-participant-count>strong\{display:none!important\}/);
 assert.match(css,/\[data-live-participants\],\s*\.projection-participant-count \[data-simulated-participants\]/);
});
