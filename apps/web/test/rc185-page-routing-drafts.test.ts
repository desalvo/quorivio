import test from 'node:test';
import assert from 'node:assert/strict';
import {pageDraftFromActivity,pageDraftSignature} from '../src/page-draft.ts';
import {mergePageDrafts} from '../src/page-merge.ts';
import {createPageDraftBackup,parsePageDraftBackup} from '../src/page-draft-recovery.ts';
const session='571e7c5d-3764-4b18-aa55-1b3802d83fb0';
const page='835cf3ac-a960-4e0d-bb20-c4a3fd82887e';
const audience='b7f4f28c-b829-4ae5-8d89-6fa07bb39b13';
const base=pageDraftFromActivity({page_design:{widgets:[]},result_design:{}});
test('per-page audience assignment and presenter skip are durable draft fields',()=>{
 const activity={page_design:{widgets:[],audiencePageId:audience,presenterHidden:true},result_design:{}};
 const draft=pageDraftFromActivity(activity);
 assert.equal(draft.audiencePageId,audience);
 assert.equal(draft.presenterHidden,true);
 assert.notEqual(pageDraftSignature(draft),pageDraftSignature(base));
 const backup=createPageDraftBackup(session,page,2,draft,base);
 const restored=parsePageDraftBackup(JSON.stringify(backup),session,page);
 assert.equal(restored.draft.audiencePageId,audience);
 assert.equal(restored.draft.presenterHidden,true);
});
test('collaborators editing audience assignment concurrently see an explicit merge conflict',()=>{
 const local={...base,audiencePageId:audience};
 const remote={...base,audiencePageId:session};
 const merged=mergePageDrafts(base,local,remote);
 assert.ok(merged.conflicts.some(x=>x.path==='/audiencePageId'));
 const fixed=mergePageDrafts(base,local,remote,{'/audiencePageId':'local'});
 assert.equal(fixed.draft.audiencePageId,audience);
});
test('editing skip flag and audience mapping independently merges without conflict',()=>{
 const local={...base,presenterHidden:true};
 const remote={...base,audiencePageId:audience};
 const merged=mergePageDrafts(base,local,remote);
 assert.equal(merged.conflicts.length,0);
 assert.equal(merged.draft.presenterHidden,true);
 assert.equal(merged.draft.audiencePageId,audience);
});
