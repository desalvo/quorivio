import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {capturePageReactionWidgetCounts} from '../src/presentation-export-reactions.ts';
import {exportFileName} from '../src/presentation-export-names.ts';

test('page-scoped reactions are mapped only onto their own authored reaction widgets',()=>{
 const pages=[
  {portable_id:'page-a',page_design:{widgets:[{kind:'reactions',id:'emoji-one'},{kind:'text',id:'text'},{kind:'reactions',id:'emoji-two'},{kind:'reactions',id:'emoji-one'}]}},
  {portable_id:'page-b',page_design:{widgets:[{kind:'reactions',id:'emoji-other'}]}},
  {portable_id:'page-c',page_design:{widgets:[{kind:'text',id:'none'}]}}
 ];
 const actual=capturePageReactionWidgetCounts(pages,[
  {activity_id:'page-a',emoji:'👍',count:3,participant_id:'SECRET'},
  {activity_id:'page-b',emoji:'👎',count:1},
  {activity_id:'page-c',emoji:'👍',count:7},
  {activity_id:'outside',emoji:'👍',count:8},
  {activity_id:'page-a',emoji:'👍',count:-1}
 ]);
 assert.deepEqual(actual,[
  {activity_id:'page-a',widget_id:'emoji-one',option_id:'👍',count:3},
  {activity_id:'page-a',widget_id:'emoji-two',option_id:'👍',count:3},
  {activity_id:'page-b',widget_id:'emoji-other',option_id:'👎',count:1}
 ]);
 assert.ok(!JSON.stringify(actual).includes('SECRET'));
});

test('invalid counts never escape into the captured presentation',()=>{
 const pages=[{portable_id:'page',page_design:{widgets:[{kind:'reactions',id:'reactions'}]}}];
 const rows=[{activity_id:'page',emoji:'👍',count:0},{activity_id:'page',emoji:'👎',count:1.2},{activity_id:'page',emoji:'👍',count:'3'},{activity_id:'page',emoji:'👍',count:-10}];
 assert.deepEqual(capturePageReactionWidgetCounts(pages,rows),[{activity_id:'page',widget_id:'reactions',option_id:'👍',count:0}]);
 assert.deepEqual(capturePageReactionWidgetCounts(pages,null),[]);
});

test('reaction export enforces a size bound before creating a giant capture JSON',()=>{
 const pages=[{portable_id:'page',page_design:{widgets:Array.from({length:100},(_,i)=>({kind:'reactions',id:'w'+i}))}}];
 const rows=Array.from({length:101},(_,i)=>({activity_id:'page',emoji:String(i),count:1}));
 assert.throws(()=>capturePageReactionWidgetCounts(pages,rows),/visual_export_reaction_limit/);
});

test('server export reuses authorized snapshot and never references absent page_reactions.widget_id',()=>{
 const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
 const schema=readFileSync(new URL('../src/schema.sql',import.meta.url),'utf8');
 const exportBlock=server.split('async function servePresentationExport(')[1].split("app.get('/api/sessions/:id/export.pptx'")[0];
 assert.match(schema,/CREATE TABLE IF NOT EXISTS page_reactions \(/);
 assert.doesNotMatch(schema,/ALTER TABLE page_reactions ADD COLUMN IF NOT EXISTS widget_id/);
 assert.doesNotMatch(exportBlock,/FROM page_reactions/);
 assert.match(exportBlock,/capturePageReactionWidgetCounts\(pptxDefinition\.activities,aggregated\?\.reactions\)/);
 assert.match(exportBlock,/visual_export_renderer_failed/);
 assert.match(exportBlock,/res\.status\(502\)/);
});

test('sidebar exports remain authenticated and never navigate to a raw API error page',()=>{
 const web=readFileSync(new URL('../../web/src/main.tsx',import.meta.url),'utf8');
 const sidebar=web.split('className="presentation-exports"')[1].split('</div>')[0];
 for(const view of ['presenter','participant'] as const)for(const format of ['pdf','pptx'] as const){
  assert.match(sidebar,new RegExp("downloadSelectedPresentation\\('"+view+"','"+format+"'\\)"));
  assert.match(exportFileName('Sessione prova',view,format),/Sessione prova - (presentatore|partecipante)\.(pdf|pptx)$/);
 }
 assert.doesNotMatch(sidebar,/<a\b[^>]*href=/);
 const handler=web.split('async function downloadSelectedPresentation(')[1].split('async function exportSelectedSessionLocal(')[0];
 assert.match(handler,/await authenticatedFetch\(/);
 assert.match(handler,/credentials:'include'/);
 assert.match(handler,/response\.status===401/);
 assert.match(handler,/setSidebarBusy\(false\)/);
 assert.match(handler,/URL\.createObjectURL\(blob\)/);
});
