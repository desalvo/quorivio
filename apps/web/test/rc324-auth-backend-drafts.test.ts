import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const api=readFileSync(new URL('../../api/src/auth-backends.ts',import.meta.url),'utf8');
const server=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');
const ui=readFileSync(new URL('../src/admin-auth-backends.tsx',import.meta.url),'utf8');

test('RC324: draft backend probes reuse Save validation but never persist a draft',()=>{
 assert.match(api,/export async function prepareAuthBackend\(/);
 assert.match(api,/const revised=await prepareAuthBackend\(db,secret,id,input\)/);
 assert.match(api,/const b=draft===undefined\?saved!:await prepareAuthBackend\(db,secret,id,draft\)/);
 assert.match(api,/if\(draft===undefined\)await db\.query\('UPDATE auth_backends SET last_tested_at=now\(\) WHERE id=\$1'/);
 assert.match(api,/return \{ok:true,scope,preview:draft!==undefined\}/);
 // The only write of encrypted configuration stays inside Save, never Test.
 const testBody=api.split('export async function testAuthBackend(',2)[1];
 assert.doesNotMatch(testBody,/INSERT INTO auth_backends|UPDATE auth_backends SET enabled/);
});

test('RC324: both saved and draft backend tests remain restricted to platform admins',()=>{
 const route=server.split("app.post('/api/admin/auth/backends/:id/test'",2)[1].split("app.get('/api/admin/settings'",1)[0];
 assert.match(route,/requireAuth,requireAdmin/);
 assert.match(route,/Object\.keys\(req\.body\)\.length/);
 assert.match(route,/testAuthBackend\(db,secret,req\.params\.id,draft\)/);
 assert.match(route,/Cache-Control','private, no-store'/);
 assert.match(route,/backend_test_failed/);
});

test('RC324: panel tests edited configuration without secretly saving or discarding other drafts',()=>{
 assert.match(ui,/const preview=Boolean\(drafts\[selected\]\)\|\|!existing/);
 assert.match(ui,/const payload=preview\?/);
 assert.match(ui,/config:item\.config/);
 assert.match(ui,/result\.preview\?'Test della bozza riuscito \(non salvata\)/);
 assert.match(ui,/await refresh\(false\)/);
 assert.match(ui,/delete next\[item\.id\]/);
 assert.match(ui,/window\.confirm\('Ricaricare\?/);
 assert.match(ui,/Testa bozza senza salvare/);
 assert.match(ui,/Ultimo test salvato/);
});
