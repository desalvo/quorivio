import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
test('restarting a page timer requires an explicit preservation choice',()=>{
 assert.match(src,/typeof req\.body\?\.clear_responses!==['"]boolean['"]/);
 assert.match(src,/if\(req\.body\.clear_responses\)\{/);
 assert.match(src,/UPDATE activities SET opened_at=now\(\)/);
});
test('starting a scheduled session renews expired attendee access and keeps cookie-scoped URLs',()=>{
 assert.match(src,/GREATEST\(expires_at,now\(\)\+interval '24 hours'\)/);
 assert.match(src,/SET current_activity_id=\$1,expires_at=GREATEST/);
 assert.match(src,/join_url:`\/join\/\$\{s\.join_secret\}`/);
 assert.match(src,/allowedLiveOrigin\(origin,publicBase\)/);
});
