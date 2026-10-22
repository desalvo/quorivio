import {test} from 'node:test';import {strict as assert} from 'node:assert';
import {encodeBase32,decodeBase32,makeTotp,verifyTotp,sealTotp,openTotp,validTotpCode,totpAuthUrl} from '../src/totp.ts';
test('RFC 6238 vector SHA1 6 digits',()=>{assert.equal(makeTotp('GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ',59000),'287082')});
test('base32 round trip',()=>{const raw=Buffer.from('hello, quorivio');assert.deepEqual(decodeBase32(encodeBase32(raw)),raw)});
test('TOTP validity, window and malformed codes',()=>{const key='GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ',code=makeTotp(key,90000);assert.ok(verifyTotp(key,code,90000));assert.ok(verifyTotp(key,code,120000));assert.equal(verifyTotp(key,code,210000),false);assert.equal(validTotpCode('12345x'),false)});
test('encrypt at rest and authenticated decrypt',()=>{const pass='x'.repeat(40),blob=sealTotp('TOPSECRET',pass);assert.ok(!blob.includes('TOPSECRET'));assert.equal(openTotp(blob,pass),'TOPSECRET');assert.throws(()=>openTotp(blob,'different password'))});
test('authenticator URI safely encodes identity',()=>{const uri=totpAuthUrl('ABCDEF','first+last@example.com');assert.ok(uri.includes('Quorivio%3Afirst%2Blast%40example.com'))});
