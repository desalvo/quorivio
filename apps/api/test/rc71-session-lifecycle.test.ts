import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validPageDesign} from '../src/domain.ts';
const api=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
const web=readFileSync(new URL('../../web/src/main.tsx',import.meta.url),'utf8');

test('independent reaction icon size is bounded and the profile text stays server-validated',()=>{
 const base={widgets:[{id:'reaction',kind:'reactions',reactionIconSize:64},{id:'profile',kind:'profile',description:'Un messaggio personale'}]};
 assert.equal(validPageDesign(base),true);
 assert.equal(validPageDesign({widgets:[{id:'reaction',kind:'reactions',reactionIconSize:97}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'reaction',kind:'reactions',reactionIconSize:0}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'profile',kind:'profile',description:'x'.repeat(501)}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'text',kind:'text',reactionIconSize:64}]}),false);
});
test('revisiting live pages does not restart countdown and manual restart is separate',()=>{
 assert.match(api,/UPDATE activities SET status='open',opened_at=COALESCE\(opened_at,now\(\)\)/);
 const begin=api.indexOf("app.post('/api/sessions/:id/activities/:aid/restart-timer'");
 const end=api.indexOf("app.post('/api/sessions/:id/activities/:aid/close'",begin);
 assert.ok(begin>0&&end>begin);
 const handler=api.slice(begin,end);
 assert.match(handler,/confirmation!=='RESTART_PAGE_TIMER'/);
 assert.match(handler,/current_activity_id!==req\.params\.aid/);
 assert.match(handler,/status!=='active'/);
 assert.match(handler,/FOR UPDATE/);
 assert.match(handler,/DELETE FROM \$\{table\} WHERE activity_id=\$1/);
 assert.match(handler,/UPDATE activities SET opened_at=now\(\)/);
 assert.match(handler,/COMMIT/);
});
test('session reset is explicitly authorized, atomic, erases private submissions and preserves authored pages',()=>{
 const start=api.indexOf("app.post('/api/sessions/:id/reset-to-ready'");
 const end=api.indexOf("app.post('/api/sessions/:id/activities/:aid/close'",start);
 assert.ok(start>0&&end>start);
 const handler=api.slice(start,end);
 assert.match(handler,/confirmation!=='RESET_SESSION_RESULTS'/);
 assert.match(handler,/owner_id=\$2 FOR UPDATE/);
 assert.match(handler,/session_asset_file_cleanup_jobs/);
 assert.match(handler,/DELETE FROM participants/);
 assert.match(handler,/DELETE FROM live_connections/);
 assert.match(handler,/status='pending',opened_at=NULL/);
 assert.match(handler,/status='ready',current_activity_id=NULL/);
 assert.match(handler,/randomBytes\(20\)/);
 assert.doesNotMatch(handler,/DELETE FROM activities/);
 assert.match(handler,/COMMIT/);
});
test('presenter QR requires auth and does not embed any bearer credentials',()=>{
 const start=api.indexOf("app.get('/api/sessions/:id/presenter-qr'");
 const end=api.indexOf('// GDPR data lifecycle',start);
 const handler=api.slice(start,end);
 assert.match(handler,/requireAuth/);
 assert.match(handler,/await owner\(/);
 assert.match(handler,/\/screen\/\$\{encodeURIComponent\(session\.id\)\}/);
 assert.doesNotMatch(handler,/auth_secret|join_secret|token=/i);
});
test('live dashboard replaces rehearsal with authentic links and requires destructive confirmation',()=>{
 assert.match(web,/resetSessionToReady\(\)/);
 assert.match(web,/window\.confirm\('Riportare la sessione a non avviata/);
 assert.match(web,/session\.status==='active'\|\|snap\.session\.status==='paused'/);
 assert.match(web,/session-live-qr/);
 assert.match(web,/presenter-qr/);
 assert.match(web,/onClick=\{\(\)=>void resetSessionToReady\(\)\}/);
 assert.match(web,/onClick=\{\(\)=>void restart\(\)\}/);
});
