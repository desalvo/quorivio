import {test} from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {profilePhotoId} from '../src/profile-photo.ts';
test('only server-generated profile photo URLs are eligible for file cleanup',()=>{
 const id=randomUUID();
 assert.equal(profilePhotoId(`/api/auth/profile/photo/${id}`),id);
 for(const url of ['../private','https://example.com/photo','/api/auth/profile/photo/../../private',`/api/auth/profile/photo/${id}/more`,null,42])assert.equal(profilePhotoId(url),null);
});
