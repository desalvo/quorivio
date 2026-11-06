// RC212: execute the actual public projection from server.ts with minimal stubs.
// The test deliberately requires no npm packages and runs before npm ci.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const source=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
const start=source.indexOf('function participantSnapshot(');
const end=source.indexOf('\nconst webRoot=',start);
assert.ok(start>=0&&end>start,'participantSnapshot boundary must exist');
const untyped=source.slice(start,end).replaceAll(':any','').replaceAll(':Activity','');
const participantSnapshot=runInNewContext(`(${untyped})`,{
  publicActivity:(activity:{id:string;title?:string})=>({id:activity.id,title:activity.title}),
}) as (data:unknown)=>any;

function fixture(){
  return {
    session:{id:'session-1',title:'Live',status:'active',current_activity_id:'audience-1',
      presenter_activity_id:'presenter-2',show_results:true,join_secret:'private'},
    activities:[
      {id:'hidden-0',page_design:{presenterHidden:true},status:'closed'},
      {id:'presenter-1',page_design:{},status:'closed'},
      {id:'presenter-2',page_design:{},status:'closed'},
      {id:'audience-1',page_design:{presenterHidden:true},status:'open',title:'Audience'},
    ],
    results:[{activity_id:'presenter-2',option_id:'p',count:99},{activity_id:'audience-1',option_id:'a',count:5}],
    totals:[{activity_id:'presenter-2',count:99},{activity_id:'audience-1',count:5}],
  };
}

test('participant sees presenter visible ordinal without presenter page ID or hidden content',()=>{
  const output=participantSnapshot(fixture());
  assert.equal(output.session.presenter_page_number,2);
  assert.equal(output.session.current_activity_id,'audience-1');
  assert.ok(!Object.hasOwn(output.session,'presenter_activity_id'));
  assert.ok(!Object.hasOwn(output.session,'join_secret'));
  assert.deepEqual(Array.from(output.activities,(a:any)=>a.id),['audience-1']);
  assert.deepEqual(Array.from(output.results,(a:any)=>a.activity_id),['audience-1']);
  assert.deepEqual(Array.from(output.totals,(a:any)=>a.activity_id),['audience-1']);
  assert.doesNotMatch(JSON.stringify(output),/presenter-2|hidden-0|private/);
});

test('participant cannot see an unopened or paused audience page',()=>{
  const data=fixture();
  data.activities[data.activities.length-1].status='closed';
  let output=participantSnapshot(data);
  assert.equal(output.session.current_activity_id,null);
  assert.equal(output.activities.length,0);
  assert.equal(output.results.length,0);
  data.activities[data.activities.length-1].status='open';
  data.session.status='paused';
  output=participantSnapshot(data);
  assert.equal(output.session.current_activity_id,null);
  assert.equal(output.activities.length,0);
});

test('presenter hidden pages do not create gaps in participant footer numbering',()=>{
  const data=fixture();
  data.session.presenter_activity_id='presenter-1';
  assert.equal(participantSnapshot(data).session.presenter_page_number,1);
  data.session.presenter_activity_id='presenter-2';
  assert.equal(participantSnapshot(data).session.presenter_page_number,2);
  assert.equal(participantSnapshot(data).session.current_activity_id,'audience-1');
});

test('hide anonymous statistics when session result sharing is disabled',()=>{
  const data=fixture();
  data.session.show_results=false;
  const output=participantSnapshot(data);
  assert.equal(output.results.length,0);
  assert.equal(output.totals.length,0);
});
