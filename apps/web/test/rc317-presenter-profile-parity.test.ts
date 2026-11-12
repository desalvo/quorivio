import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validPageDesign} from '../../api/src/domain.ts';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'../src');
const main=readFileSync(resolve(root,'main.tsx'),'utf8');
const profile={id:'profile1',kind:'profile',showEmail:false,showProfileName:true,showProfilePhoto:true,showProfileDescription:false};

test('RC317 profile field settings are accepted only for presenter profile widgets',()=>{
 assert.equal(validPageDesign({widgets:[profile]}),true);
 for(const key of ['showProfileName','showProfilePhoto','showProfileDescription'] as const){
  assert.equal(validPageDesign({widgets:[{...profile,[key]:'yes'}]}),false,key);
  assert.equal(validPageDesign({widgets:[{id:'text1',kind:'text',[key]:true}]}),false,key);
 }
});
test('RC317 editor uses authenticated presenter endpoint before publication',()=>{
 assert.match(main,/usePrivateProfile=\{w.kind==='profile'\}/);
 assert.match(main,/request<any\[\]>\(`\/sessions\/\$\{encodeURIComponent\(sessionId\)\}\/presenter-profiles`\)/);
 assert.match(main,/profiles.find\(p=>p.is_owner\)/);
 assert.match(main,/profile\?\.photo_url\|\|profile\?\.profile_photo_url/);
});
test('RC317 format widget controls photo, name, email and description with public email opt-in',()=>{
 for(const label of ['Mostra foto presentatore','Mostra nome presentatore','Mostra email presentatore','Mostra descrizione presentatore'])assert.ok(main.includes(label),label);
 assert.match(main,/showEmail:widget.showEmail===true/);
 assert.match(main,/showEmail===true&&profile.email/);
 assert.match(main,/showProfilePhoto!==false&&photo/);
 assert.match(main,/showProfileName!==false&&/);
});
