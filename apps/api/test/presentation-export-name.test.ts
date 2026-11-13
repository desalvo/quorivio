import test from 'node:test';
import assert from 'node:assert/strict';
import {exportFileName,presentationContentDisposition,presentationExportView} from '../src/presentation-export-names.ts';
import {readFileSync} from 'node:fs';

test('four exports use session name and exact presenter/participant suffix',()=>{
 for(const format of ['pdf','pptx'] as const){
  assert.equal(exportFileName('Seminario CERN', 'presenter',format),`Seminario CERN - presentatore.${format}`);
  assert.equal(exportFileName('Seminario CERN', 'participant',format),`Seminario CERN - partecipante.${format}`);
 }
});
test('filename is safe for HTTP headers and preserves Italian accents',()=>{
 const header=presentationContentDisposition('  L’estate: prova/avvio\r\nX-Injected: 1  ','participant','pdf');
 assert.ok(header.startsWith('attachment; filename='));
 assert.ok(header.includes('filename*=UTF-8'));
 assert.ok(!header.includes('\r')&&!header.includes('\n'));
 assert.ok(!header.includes('prova/avvio'));
 assert.match(decodeURIComponent(header.split("filename*=UTF-8''")[1]),/partecipante\.pdf$/);
 assert.equal(exportFileName('\0<>/?*','presenter','pptx').endsWith('presentatore.pptx'),true);
});
test('strict viewer parser rejects malformed queries',()=>{
 assert.equal(presentationExportView('presenter'),'presenter');
 assert.equal(presentationExportView('participant'),'participant');
 for(const invalid of [[],['presenter','participant'],'administrator','',null,undefined])assert.equal(presentationExportView(invalid),null);
});
test('presenter and audience decks route hidden mapped pages separately',()=>{
 const a={id:'a',page_design:{audiencePageId:'hidden'}},h={id:'hidden',page_design:{presenterHidden:true}},b={id:'b',page_design:{}};
  const code=readFileSync(new URL('../src/presentation-export-snapshot.ts',import.meta.url),'utf8');
 assert.match(code,/presenterPages\(pages\)/);
 assert.match(code,/audienceForPresenter\(pages,page\)/);
});
test('visual snapshot is sourced only from authored metadata and aggregate statistics',()=>{
 const code=readFileSync(new URL('../src/presentation-export-snapshot.ts',import.meta.url),'utf8');
 assert.match(code,/definition\.activities\.map/);
 assert.match(code,/delete session\.join_secret/);
 assert.match(code,/capture_widget_results/);
});
