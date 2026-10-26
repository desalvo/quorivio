import {test} from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {publicPresenterProfiles} from '../src/profile-photo.ts';

test('public presenter profiles expose session-scoped photo links, never private storage URLs',()=>{
 const id=randomUUID(),photo=randomUUID();
 const result=publicPresenterProfiles([{id,name:'Presenter',profile_photo_url:`/api/auth/profile/photo/${photo}`}],'a/b?x=1');
 assert.deepEqual(result,[{id,name:'Presenter',photo_url:`/api/join/a%2Fb%3Fx%3D1/presenters/${id}/photo`}]);
 assert.equal(JSON.stringify(result).includes('/api/auth/profile/photo'),false);
});
test('missing and malformed profile photos do not create public links',()=>{
 const id=randomUUID();
 for(const url of [null,'',false,'https://attacker.invalid/photo','/api/auth/profile/photo/../../etc/passwd','/api/auth/profile/photo/not-a-uuid']){
  const result=publicPresenterProfiles([{id,name:'Presenter',profile_photo_url:url}],'join');
  assert.equal(result[0].photo_url,null);
 }
});
test('public profile projection preserves presenter order without leaking extra database columns',()=>{
 const rows=[{id:randomUUID(),name:'One',profile_photo_url:null,email:'private@example.org'},
 {id:randomUUID(),name:'Two',profile_photo_url:null,role:'platform_admin'}];
 const result=publicPresenterProfiles(rows,'join');
 assert.deepEqual(result.map(x=>x.name),['One','Two']);
 assert.deepEqual(Object.keys(result[0]),['id','name','photo_url']);
 assert.deepEqual(Object.keys(result[1]),['id','name','photo_url']);
});
