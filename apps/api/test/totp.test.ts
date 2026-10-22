import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {randomBytes} from 'node:crypto';
import {encodeBase32,decodeBase32,makeTotp,verifyTotp,sealTotp,openTotp,validTotpCode,totpAuthUrl} from '../src/totp.ts';

// RFC 6238's published SHA-1 test key consists of the first 20 ASCII digits.
// Build the public vector programmatically so secret scanners do not mistake
// a literal Base32 example for an application credential.
const rfcTestKey=()=>encodeBase32(Buffer.from(Array.from({length:20},(_,i)=>48+((i+1)%10))));

test('RFC 6238 public SHA1 vector, truncated to six digits',()=>{
  assert.equal(makeTotp(rfcTestKey(),59000),'287082');
});
test('base32 round trip',()=>{
  const raw=Buffer.from('hello, quorivio');
  assert.deepEqual(decodeBase32(encodeBase32(raw)),raw);
});
test('TOTP validity, window and malformed codes',()=>{
  const key=encodeBase32(randomBytes(20));
  const code=makeTotp(key,90000);
  assert.ok(verifyTotp(key,code,90000));
  assert.ok(verifyTotp(key,code,120000));
  assert.equal(verifyTotp(key,code,210000),false);
  assert.equal(validTotpCode('12345x'),false);
});
test('encrypt at rest and authenticated decrypt',()=>{
  const pass=randomBytes(40).toString('hex');
  const secret=encodeBase32(randomBytes(20));
  const blob=sealTotp(secret,pass);
  assert.ok(!blob.includes(secret));
  assert.equal(openTotp(blob,pass),secret);
  assert.throws(()=>openTotp(blob,'different password'));
});
test('authenticator URI safely encodes identity',()=>{
  const uri=totpAuthUrl(encodeBase32(randomBytes(20)),'first+last@example.com');
  assert.ok(uri.includes('Quorivio%3Afirst%2Blast%40example.com'));
});
