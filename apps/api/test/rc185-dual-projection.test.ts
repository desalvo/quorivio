import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validPageDesign} from '../src/domain.ts';
import {firstPresenterPage,presenterPages,audienceForPresenter,validAudienceMapping,validPortablePageRouting,remapPortablePageRouting} from '../src/presentation-routing.ts';
const questionId='571e7c5d-3764-4b18-aa55-1b3802d83fb0';
const resultsId='835cf3ac-a960-4e0d-bb20-c4a3fd82887e';
const newQuestionId='b7f4f28c-b829-4ae5-8d89-6fa07bb39b13';
const q={id:questionId,page_design:{presenterHidden:true,widgets:[{id:'q',kind:'question',label:'Quale risposta?',options:[{id:'one',label:'Uno'},{id:'two',label:'Due'}]}]}};
const r={id:resultsId,page_design:{audiencePageId:questionId,widgets:[{id:'stats',kind:'results-button',targetActivityId:questionId,targetWidgetId:'q'}]}};

test('presenter can skip question slide while audience votes on it',()=>{
 assert.deepEqual(presenterPages([q,r]),[r]);
 assert.equal(firstPresenterPage([q,r]),r);
 assert.equal(audienceForPresenter([q,r],r),q);
 assert.equal(validAudienceMapping([q,r],r),true);
 assert.equal(validAudienceMapping([r],r),false);
 assert.equal(audienceForPresenter([r],r),null);
 assert.equal(audienceForPresenter([r],{id:resultsId,page_design:{}})?.id,resultsId);
});
test('cross-page results, audience mapping and presenter visibility have strict types',()=>{
 assert.equal(validPageDesign(r.page_design),true);
 assert.equal(validPageDesign(q.page_design),true);
 assert.equal(validPageDesign({...r.page_design,audiencePageId:'../../other'}),false);
 assert.equal(validPageDesign({...r.page_design,presenterHidden:'yes'}),false);
 assert.equal(validPageDesign({widgets:[{id:'stats',kind:'results-button',targetActivityId:'bad-id',targetWidgetId:'q'}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'stats',kind:'results-button',targetActivityId:questionId,targetWidgetId:'q'}]}),true);
});
test('portable sessions remap BOTH audience routing and result source across page IDs',()=>{
 const pages=[{portable_id:q.id,page_design:q.page_design},{portable_id:r.id,page_design:r.page_design}];
 assert.equal(validPortablePageRouting(pages),true);
 const map=new Map([[questionId,newQuestionId],[resultsId,resultsId]]);
 const remapped=remapPortablePageRouting(r.page_design,map);
 assert.equal(remapped.audiencePageId,newQuestionId);
 assert.equal(remapped.widgets[0].targetActivityId,newQuestionId);
 assert.equal(r.page_design.audiencePageId,questionId);
 assert.equal(validPortablePageRouting([{portable_id:resultsId,page_design:r.page_design}]),false);
 assert.equal(validPortablePageRouting([...pages,pages[1]]),false);
 assert.throws(()=>remapPortablePageRouting(r.page_design,new Map()),/missing_portable_audience_page/);
 assert.equal(validPortablePageRouting([{portable_id:questionId,page_design:{widgets:[null]}},{portable_id:resultsId,page_design:{}}]),false);
 assert.equal(validPortablePageRouting([{portable_id:questionId,page_design:{widgets:'malformed'}},{portable_id:resultsId,page_design:{widgets:[{id:'result',kind:'results-button',targetActivityId:questionId,targetWidgetId:'q'}]}}]),false);
});
test('cross-page widget source cannot refer outside archive or to other kinds',()=>{
 assert.equal(validPortablePageRouting([{portable_id:questionId,page_design:{widgets:[{id:'text',kind:'text'}]}},{portable_id:resultsId,page_design:{widgets:[{id:'result',kind:'results-button',targetActivityId:questionId,targetWidgetId:'text'}]}}]),false);
 assert.equal(validPortablePageRouting([{portable_id:questionId,page_design:{widgets:[]}},{portable_id:resultsId,page_design:{widgets:[{id:'result',kind:'results-button',targetActivityId:questionId,targetWidgetId:'missing'}]}}]),false);
});
test('server switches audience page atomically while presenter projection remains independent',()=>{
 const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
 assert.match(server,/UPDATE sessions SET current_activity_id=\$1,presenter_activity_id=\$3/);
 assert.match(server,/await cx\.query\('COMMIT'\);begun=false;await broadcast/);
 assert.match(server,/audience_page_not_in_session/);
 assert.match(server,/const locked=await cx\.query\('SELECT status FROM sessions WHERE id=\$1 FOR UPDATE'/);
 assert.match(server,/result_source_not_in_session/);
 assert.match(server,/expected_presenter_activity_id/);
 const participant=server.slice(server.indexOf('function participantSnapshot('),server.indexOf('function participantSnapshot(')+750);
 // RC206: the private presenter id may be read to compute the shared footer
 // ordinal, but must never appear as a property in the PUBLIC snapshot.
 const publicReturn=participant.slice(participant.indexOf('return {session:{'));
 assert.doesNotMatch(publicReturn,/presenter_activity_id\s*:/);
 assert.match(publicReturn,/presenter_page_number:presenterNumber/);
 assert.match(publicReturn,/current_activity_id/);
});
