import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {capturePageRatingWidgetCounts,PRESENTATION_EXPORT_RATINGS_SQL} from '../src/presentation-export-ratings.ts';

test('rating counts map exclusively to authored rating widgets on their own page',()=>{
 const pages=[
  {portable_id:'a',page_design:{widgets:[{kind:'rating',id:'r1'},{kind:'text',id:'t1'},{kind:'rating',id:'r2'},{kind:'rating',id:'r1'}]}},
  {portable_id:'b',page_design:{widgets:[{kind:'rating',id:'r3'}]}},
  {portable_id:'c',page_design:{widgets:[{kind:'text',id:'t2'}]}}
 ];
 const result=capturePageRatingWidgetCounts(pages,[
  {activity_id:'a',option_id:'0',count:3,participant_id:'SECRET'},
  {activity_id:'b',option_id:'9',count:2},
  {activity_id:'c',option_id:'8',count:3},
  {activity_id:'unknown',option_id:'8',count:9}
 ]);
 assert.deepEqual(result,[
  {activity_id:'a',widget_id:'r1',option_id:'0',count:3},
  {activity_id:'a',widget_id:'r2',option_id:'0',count:3},
  {activity_id:'b',widget_id:'r3',option_id:'9',count:2}
 ]);
 assert.ok(!JSON.stringify(result).includes('SECRET'));
});

test('invalid scores and counts cannot enter the captured document',()=>{
 const page=[{portable_id:'p',page_design:{widgets:[{kind:'rating',id:'r'}]}}];
 const result=capturePageRatingWidgetCounts(page,[
  {activity_id:'p',option_id:'0',count:0},
  {activity_id:'p',option_id:'10',count:1},
  {activity_id:'p',option_id:'11',count:1},
  {activity_id:'p',option_id:'00',count:1},
  {activity_id:'p',option_id:'5',count:'2'},
  {activity_id:'p',option_id:'5',count:-1},
  {activity_id:'p',option_id:'5',count:1.5}
 ]);
 assert.deepEqual(result,[
  {activity_id:'p',widget_id:'r',option_id:'0',count:0},
  {activity_id:'p',widget_id:'r',option_id:'10',count:1}
 ]);
 assert.deepEqual(capturePageRatingWidgetCounts(page,{}),[]);
});

test('rating export has a strict bounded aggregate',()=>{
 const pages=[{portable_id:'p',page_design:{widgets:Array.from({length:100},(_,i)=>({kind:'rating',id:'r'+i}))}}];
 const totals=Array.from({length:101},(_,i)=>({activity_id:'p',option_id:String(i%10),count:1}));
 assert.throws(()=>capturePageRatingWidgetCounts(pages,totals),/visual_export_rating_limit/);
});

test('export SQL uses real page_ratings schema and is executed by the endpoint',()=>{
 const schema=readFileSync(new URL('../src/schema.sql',import.meta.url),'utf8');
 const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
 const columns=schema.split('CREATE TABLE IF NOT EXISTS page_ratings(')[1].split(');')[0];
 const block=server.split('async function servePresentationExport(')[1].split("app.get('/api/sessions/:id/export.pptx'")[0];
 assert.match(columns,/\bscore integer NOT NULL\b/);
 assert.doesNotMatch(columns,/\bwidget_id\b/);
 assert.doesNotMatch(PRESENTATION_EXPORT_RATINGS_SQL,/\bwidget_id\b|\bparticipant_id\b/);
 assert.match(PRESENTATION_EXPORT_RATINGS_SQL,/GROUP BY activity_id,score/);
 assert.match(block,/db.query\(PRESENTATION_EXPORT_RATINGS_SQL,\[s.id\]\)/);
 assert.match(block,/capturePageRatingWidgetCounts\(pptxDefinition.activities,ratingCounts.rows\)/);
});
