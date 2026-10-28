import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
function route(begin:string,end:string):string{
 const start=server.indexOf(begin);
 const stop=server.indexOf(end,start+begin.length);
 assert.ok(start>=0&&stop>start,`missing route boundary: ${begin}`);
 return server.slice(start,stop);
}
const widget=route("app.post('/api/join/:code/activities/:aid/widgets/:wid/respond'","app.get('/api/sessions/:id/widget-answers'");
const legacy=route("app.post('/api/join/:code/respond'","server.on('upgrade'");
const topic=route("app.post('/api/join/:code/activities/:aid/topic-widgets/:wid/questions'","app.get('/api/sessions/:id/activities/:aid/topic-widgets/:wid/questions'");
const widgetRank=route("app.get('/api/sessions/:id/activities/:aid/widgets/:wid/timed-leaderboard'","app.get('/api/sessions/:id/activities/:aid/timed-leaderboard'");
const legacyRank=route("app.get('/api/sessions/:id/activities/:aid/timed-leaderboard'","app.post('/api/join/:code/respond'");

test('widget identity resolution never holds a database client',()=>{
 assert.ok(widget.indexOf('audienceIdentity(')<widget.indexOf('cx=await db.connect()'));
 assert.ok(widget.indexOf('cx.release();cx=undefined')<widget.indexOf('await notifyAudience('));
});
test('topic question limit locks the participant after page fencing',()=>{
 assert.ok(topic.indexOf('audienceIdentity(')<topic.indexOf('cx=await db.connect()'));
 assert.ok(topic.indexOf('lockAudiencePage(')<topic.indexOf('FROM participants WHERE id=$1 AND session_id=$2 FOR UPDATE'));
 assert.ok(topic.indexOf('FOR UPDATE')<topic.indexOf('SELECT count(*)::int AS n FROM topic_widget_questions'));
 assert.ok(topic.indexOf('SELECT count(*)::int AS n FROM topic_widget_questions')<topic.indexOf('INSERT INTO topic_widget_questions'));
 assert.ok(topic.indexOf('cx.release();cx=undefined')<topic.indexOf('await notifyAudience('));
});
test('timed widget duplicate acknowledgement takes precedence over expired deadline',()=>{
 assert.ok(widget.includes('SELECT id FROM widget_answers WHERE activity_id=$1 AND participant_id=$2 AND widget_id=$3 AND question_id=$4 AND revision=$5'));
 assert.ok(widget.indexOf('if(existing.rowCount)')<widget.indexOf('timedDeadline('));
 assert.ok(widget.includes('already_submitted:true,question_id:questionId,revision'));
});
test('legacy quiz retries are idempotent after expiry and safe on notify failures',()=>{
 assert.ok(legacy.indexOf('if(existing.rowCount)')<legacy.indexOf('timedDeadline('));
 assert.ok(legacy.includes("act.type==='timed_quiz'?await cx.query"));
 assert.ok(legacy.indexOf('cx.release();cx=undefined')<legacy.indexOf('await notifyAudience('));
});
test('both presenter-only rankings compute identical elapsed times as ties before paging',()=>{
 for(const ranking of [widgetRank,legacyRank]){
  assert.ok(ranking.includes('rank() OVER (ORDER BY'));
  assert.ok(ranking.indexOf('rank() OVER (ORDER BY')<ranking.indexOf('LIMIT'));
  assert.ok(!ranking.includes('rank:(page-1)'));
  assert.ok(ranking.includes('await owner('));
 }
 assert.ok(widgetRank.includes('w.revision=$3'));
 assert.ok(legacyRank.includes('r.invalidated_at IS NULL'));
});
