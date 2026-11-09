import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {localSessionArchiveFilename,localSessionImportError,isLocalSessionArchiveMime,LOCAL_SESSION_ARCHIVE_MIME} from '../src/session-local-transfer.ts';

const app=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const api=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');

test('portable download filenames stay local, never traversal/hidden dotfiles',()=>{
 assert.equal(localSessionArchiveFilename('Workshop 2026'), 'quorivio-Workshop 2026.quo');
 assert.equal(localSessionArchiveFilename('../danger\\name:export'), 'quorivio--danger-name-export.quo');
 assert.equal(localSessionArchiveFilename(''), 'quorivio-sessione.quo');
 assert.ok(localSessionArchiveFilename('a'.repeat(500)).length<115);
});

test('sidebar import accepts only actual bounded .quo archives',()=>{
 assert.equal(localSessionImportError({name:'session.QUO',size:1024}),null);
 assert.match(localSessionImportError({name:'session.json',size:1024})||'',/Formato/);
 assert.match(localSessionImportError({name:'session.quo',size:0})||'',/vuoto/);
 assert.match(localSessionImportError({name:'session.quo',size:101*1024*1024})||'',/100 MiB/);
 assert.equal(isLocalSessionArchiveMime(LOCAL_SESSION_ARCHIVE_MIME+'; charset=binary'),true);
 assert.equal(isLocalSessionArchiveMime('application/json'),false);
});

test('sidebar provides both export and import, even outside an opened session',()=>{
 assert.match(app,/aria-label="Navigazione funzionalità"[\s\S]*?Importa sessione da locale/);
 assert.match(app,/aria-label="Azioni della sessione corrente"[\s\S]*?Esporta in locale \(\.quo\)/);
 assert.match(app,/aria-label="Azioni della sessione corrente"[\s\S]*?Importa da locale \(\.quo\)/);
 assert.match(app,/localSessionImportRef\.current\?\.click\(\)/);
 assert.match(app,/type="file" accept="\.quo,application\/vnd\.quorivio\.session\+zip" hidden/);
});

test('export rejects server errors and JSON before creating a download',()=>{
 const exportAction=app.slice(app.indexOf('async function exportSelectedSessionLocal()'),app.indexOf('async function importSessionFile(',app.indexOf('async function exportSelectedSessionLocal()')));
 assert.match(exportAction,/authenticatedFetch\(/);
 assert.match(exportAction,/if\(!response\.ok\)/);
 assert.match(exportAction,/isLocalSessionArchiveMime\(response\.headers\.get\('Content-Type'\)\)/);
 assert.match(exportAction,/blob\.size<22\|\|blob\.size>LOCAL_SESSION_ARCHIVE_MAX_BYTES/);
 assert.match(exportAction,/URL\.revokeObjectURL/);
 assert.match(exportAction,/setSidebarBusy\(true\)/);
 assert.match(exportAction,/finally\{setSidebarBusy\(false\)\}/);
});

test('import never overwrites the existing session, and server verifies uploaded bytes',()=>{
 const begin=app.indexOf('async function importQuorivioBundle(');
 const end=app.indexOf('async function exportSelectedSessionLocal(',begin);
 const transfer=app.slice(begin,end);
 assert.match(transfer,/localSessionImportError\(file\)/);
 assert.match(transfer,/authenticatedFetch\('\/api\/sessions\/import\.quo'/);
 assert.match(transfer,/if\(!response\.ok\)throw/);
 assert.match(transfer,/setSelected\(result\.id\)/);
 assert.doesNotMatch(transfer,/PATCH|PUT|DELETE/);
 assert.match(api,/app\.post\('\/api\/sessions\/import\.quo',requireAuth,requirePresenter/);
 assert.match(api,/decodeBundle\(await readFile\(upload\.destination\)\)/);
 assert.match(api,/createFromPortable\(definition,auth\(req\)!,importDir,true\)/);
});

test('full local export includes unreferenced private attachments but never participant uploads',()=>{
 const begin=api.indexOf("app.get('/api/sessions/:id/export.quo'");
 const end=api.indexOf("app.post('/api/sessions/import.quo'",begin);
 const transfer=api.slice(begin,end);
 assert.match(transfer,/participant_id IS NULL ORDER BY id/);
 assert.doesNotMatch(transfer,/id=ANY\(/);
 assert.match(transfer,/missing_session_assets/);
 assert.match(transfer,/encodeBundle\(/);
 assert.match(api,/session\.schedule_dates=.*session_schedule_dates/);
 assert.match(api,/session\.appointments=.*session_appointments/);
 assert.match(api,/definition\.session\.appointments\|\|\[\]/);
 assert.doesNotMatch(transfer,/participant_answers|response_votes|join_secret/);
});
