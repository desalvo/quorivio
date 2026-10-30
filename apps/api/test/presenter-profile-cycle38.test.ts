import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {publicPresenterProfiles} from '../src/profile-photo.ts';
import {validPageDesign} from '../src/domain.ts';

test('public email is excluded by default and enabled only for explicitly opted-in presenter ID',()=>{
 const profiles=[{id:'a',name:'Giulia Rossi',email:'giulia@example.org',profile_photo_url:null},{id:'b',name:'Mario Verdi',email:'mario@example.org',profile_photo_url:null}];
 const hidden=publicPresenterProfiles(profiles,'join');
 assert.equal('email' in hidden[0],false);
 assert.equal('email' in hidden[1],false);
 const exposed=publicPresenterProfiles(profiles,'join',new Set(['a']));
 assert.deepEqual(exposed[0],{id:'a',name:'Giulia Rossi',email:'giulia@example.org',photo_url:null});
 assert.equal('email' in exposed[1],false);
});
test('email publication is permitted only for profile widgets and explicit boolean consent',()=>{
 assert.equal(validPageDesign({widgets:[{id:'profile',kind:'profile',showEmail:true}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'profile',kind:'profile',showEmail:false}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'question',kind:'question',showEmail:true}]}),false);
 assert.equal(validPageDesign({widgets:[{id:'profile',kind:'profile',showEmail:'true'}]}),false);
 const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
 assert.match(server,/w\.kind==='profile'&&w\.showEmail===true/);
 assert.match(server,/publicPresenterProfiles\(profiles\.rows,req\.params\.code,publicEmailIds\)/);
});
