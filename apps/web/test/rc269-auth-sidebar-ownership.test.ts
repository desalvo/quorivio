import {test} from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const api=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');
test('expired presenter auth redirects once; multipart and fetch APIs also use the guard',()=>{
 // Expired credentials render sign-in in-app; navigation would re-trigger
 // a network fetch loop and eventually hit the API rate limiter.
 assert.match(ui,/window\.history\.replaceState/);
 assert.match(ui,/window\.dispatchEvent\(new Event\('quorivio:authentication-expired'\)\)/);
 assert.doesNotMatch(ui,/window\.location\.(?:replace|assign|reload)\(/);
 assert.match(ui,/if\(reauthenticationRedirecting&&!authRoute&&!guestRoute\)/);
 assert.match(ui,/status===401&&\['authentication_required','session_revoked'\]/);
 assert.match(ui,/async function authenticatedFetch/);
 assert.match(ui,/authenticatedFetch\(`\/api\/sessions\//);
 assert.match(ui,/!url\.startsWith\('\/join\/'\)/);
 assert.match(ui,/!\['\/auth\/me','\/auth\/login'/);
 assert.doesNotMatch(ui,/!url\.startsWith\('\/auth\/'\)/);
});
test('blank sidebar only opens context menu on right click or long press',()=>{
 const aside=ui.match(/<aside className="page-editor-sidebar"[^\n]*/)?.[0]||'';
 assert.ok(aside);
 assert.match(aside,/onContextMenu=/);
 assert.match(aside,/onTouchStart=/);
 assert.doesNotMatch(aside,/onClick=/);
 assert.match(aside,/650/);
});
test('primary owner transfer is restricted, audited and available in UI',()=>{
 assert.match(api,/app\.post\('\/api\/sessions\/:id\/transfer-owner',requireAuth,requirePresenter/);
 assert.match(api,/current\.owner_id!==auth\(req\)/);
 assert.match(api,/BEGIN[\s\S]*?session_ownership_transfers/);
 assert.match(ui,/transferPrimaryOwner/);
 assert.match(ui,/keep_previous_as_collaborator/);
});
test('smartphone editor response choices have readable minimum 17px',()=>{
 assert.match(css,/RC269: phone editor options/);
 assert.match(css,/font-size:clamp\(17px/);
 assert.match(css,/canvas-editor-group\[data-canvas-device="phone"\]/);
});
