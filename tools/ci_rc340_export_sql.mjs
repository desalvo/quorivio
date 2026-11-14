/** Mandatory real disposable PostgreSQL execution of the exact export SQL. */
import assert from 'node:assert/strict';
import pg from 'pg';
import {PRESENTATION_EXPORT_RATINGS_SQL,capturePageRatingWidgetCounts} from '../apps/api/src/presentation-export-ratings.ts';

if(process.env.QUORIVIO_CI_VISUAL_RATINGS_PG!=='1'||!process.env.DATABASE_URL){
 throw Error('Disposable PostgreSQL acceptance must be explicitly enabled');
}
const db=new pg.Client({connectionString:process.env.DATABASE_URL,connectionTimeoutMillis:10000});
try{
 await db.connect();
 const columns=await db.query("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='page_ratings'");
 const names=new Set(columns.rows.map(row=>row.column_name));
 for(const name of ['session_id','activity_id','participant_id','score'])assert.ok(names.has(name),'missing schema column: '+name);
 assert.ok(!names.has('widget_id'),'page_ratings unexpectedly contains widget_id');
 const result=await db.query(PRESENTATION_EXPORT_RATINGS_SQL,['00000000-0000-4000-8000-000000000000']);
 assert.deepEqual(result.rows,[],'disposable zero-ID fixture should be empty');
 assert.deepEqual(capturePageRatingWidgetCounts([],result.rows),[]);
 console.log('PASS RC340: real PostgreSQL visual-export ratings query and schema contract');
}finally{
 await db.end().catch(()=>{});
}
