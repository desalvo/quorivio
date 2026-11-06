import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {canDeleteListedSession,canResetListedSession} from '../src/session-list-management.ts';

const source=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const api=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');
const owner=(status:string)=>({id:'a',status,access_role:'owner' as const});
const collaborator=(status:string)=>({id:'b',status,access_role:'collaborator' as const});

test('an owner can reset started, paused and closed sessions without opening them',()=>{
 for(const status of ['active','paused','closed'])assert.equal(canResetListedSession(owner(status)),true,status);
 for(const status of ['ready','draft'])assert.equal(canResetListedSession(owner(status)),false,status);
});
test('collaborators cannot reset or erase sessions regardless of status',()=>{
 for(const status of ['active','paused','closed','ready','draft']){
  assert.equal(canResetListedSession(collaborator(status)),false);
  assert.equal(canDeleteListedSession(collaborator(status)),false);
  assert.equal(canDeleteListedSession(owner(status)),true);
 }
});
test('list commands target their own session IDs, require confirmation and never depend on selected/open session',()=>{
 const start=source.indexOf('async function resetListedSession(session:Session)');
 const end=source.indexOf('async function duplicateSessionFrom',start);
 assert.ok(start>0&&end>start);
 const actions=source.slice(start,end);
 assert.match(actions,/window\.confirm\(/);
 assert.match(actions,/encodeURIComponent\(session\.id\)/);
 assert.match(actions,/RESET_SESSION_RESULTS/);
 assert.match(actions,/method:'DELETE'/);
 assert.match(actions,/if\(selected===session\.id\)/);
 assert.match(actions,/listSessionBusyRef\.current/);
 assert.doesNotMatch(actions,/document\.cookie|localStorage\.clear|sessionStorage\.clear/);
 assert.match(source,/aria-label=\{`Resetta la sessione \$\{s\.title\} a non avviata`\}/);
 assert.match(source,/aria-label=\{`Elimina definitivamente la sessione \$\{s\.title\}`\}/);
});
test('backend reset is transactional, owner-only and can recover closed sessions',()=>{
 const start=api.indexOf("app.post('/api/sessions/:id/reset-to-ready'");
 const end=api.indexOf("app.post('/api/sessions/:id/activities/:aid/close'",start);
 assert.ok(start>0&&end>start);
 const handler=api.slice(start,end);
 assert.match(handler,/confirmation!=='RESET_SESSION_RESULTS'/);
 assert.match(handler,/owner_id=\$2 FOR UPDATE/);
 assert.match(handler,/\['active','paused','closed'\]/);
 assert.match(handler,/DELETE FROM participants/);
 assert.match(handler,/session_asset_file_cleanup_jobs/);
 assert.match(handler,/join_secret=\$3/);
 assert.match(handler,/expires_at=GREATEST/);
 assert.match(handler,/COMMIT/);
 assert.doesNotMatch(handler,/DELETE FROM activities/);
 const deletion=api.slice(api.indexOf("app.delete('/api/sessions/:id'"),api.indexOf('// A session may be auto-purged'));
 assert.match(deletion,/owner_id!==auth\(req\)/);
 assert.match(deletion,/SESSION_DELETE_WITH_CLEANUP_SQL/);
});
