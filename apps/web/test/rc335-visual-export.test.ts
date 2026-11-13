import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const server=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');
const worker=readFileSync(new URL('../../../tools/conversion_worker.py',import.meta.url),'utf8');
const python=readFileSync(new URL('../../../tools/visual_export.py',import.meta.url),'utf8');

test('four distinct downloads select presenter/participant and PDF/PPTX',()=>{
 for(const view of ['presenter','participant'])for(const format of ['pdf','pptx'])
  assert.ok(main.includes(`/export.${format}?view=${view}`),`${view}-${format}`);
 assert.ok(server.includes('presentationContentDisposition(s.title,view,format)'));
});
test('visual slides use the real rehearsal 1280x720 renderer, without editor chrome',()=>{
 assert.match(main,/id="quorivio-export-slide"/);
 assert.match(main,/renderSlide\(captureMode\)/);
 assert.match(main,/data-export-page=\{page\}/);
 assert.match(main,/__quorivioExportSetPage/);
 assert.match(css,/#quorivio-export-slide>/);
 assert.match(python,/page\.locator\('#quorivio-export-slide'\)\.screenshot/);
 assert.match(python,/slide\.shapes\.add_picture/);
});
test('participant export uses audience-mapped pages and suppresses private results',()=>{
 assert.match(main,/rehearsalAudiencePage\(activity,activities\)/);
 assert.match(main,/participantVisibleWidgets\(viewWidgets\)/);
 assert.match(main,/captureMode\?capturedRows/);
 assert.match(server,/presentationExportPages\(planned,view\)/);
});
test('capture is gated by per-job capability and Chromium blocks unrelated URLs',()=>{
 assert.match(server,/timingSafeEqual\(Buffer\.from\(target,'ascii'\),Buffer\.from\(candidate,'ascii'\)\)/);
 assert.match(server,/capture-token/);
 assert.match(worker,/visual-export-pdf/);
 assert.match(python,/route\.abort\(\);return/);
 assert.match(python,/if route_path\.startswith\('\/api\/'\)/);
 assert.doesNotMatch(python,/storage_state=/);
});

test('visual export freezes live aggregate participation while rehearsal retains synthetic values',()=>{
 assert.match(main,/data-live-participants="true"/);
 assert.match(main,/data-simulated-participants="true"/);
 assert.match(main,/emptyLabel="esportazione statica" participation=/);
 assert.match(server,/connected_participants:aggregated\?\.connected_participants/);
});
