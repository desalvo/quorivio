import {test} from 'node:test';
import assert from 'node:assert/strict';
import {validateSettingsPatch} from '../src/platform-settings.ts';
test('platform settings patch validates the entire payload before any database write',()=>{
 assert.deepEqual(validateSettingsPatch({public_base_url:'https://quorivio.example.org',closed_session_retention_days:90,max_upload_mb:100}),{ok:true,changes:[['public_base_url','https://quorivio.example.org'],['closed_session_retention_days','90'],['max_upload_mb','100']]});
 for(const v of [{public_base_url:'https://quorivio.example.org',max_upload_mb:0},{public_base_url:'http://example.org'},{public_base_url:'https://user:pass@example.org'},{public_base_url:'https://example.org/other'},{public_base_url:'https://example.org/#frag'},{closed_session_retention_days:3651},{max_upload_mb:1.5},{max_upload_mb:'100'},null,[]])assert.equal(validateSettingsPatch(v).ok,false,JSON.stringify(v));
 assert.deepEqual(validateSettingsPatch({max_upload_mb:1}),{ok:true,changes:[['max_upload_mb','1']]});
});
