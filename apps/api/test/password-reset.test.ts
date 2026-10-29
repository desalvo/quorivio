import test from 'node:test';import assert from 'node:assert/strict';
import {generateResetToken,resetTokenDigest,normalizeResetEmail,validResetToken,validNewPassword,resetLink} from '../src/password-reset.ts';
test('reset token is random, url-safe and has fixed digest',()=>{const x=generateResetToken(),y=generateResetToken();assert.notEqual(x,y);assert.equal(validResetToken(x),true);assert.equal(resetTokenDigest(x).length,64);assert.notEqual(resetTokenDigest(x),resetTokenDigest(y))});
test('password reset input validation',()=>{assert.equal(normalizeResetEmail('  USER@Example.org '),'user@example.org');assert.equal(normalizeResetEmail('wrong'),null);assert.equal(validResetToken('wrong'),false);assert.equal(validNewPassword('123456789012'),true);assert.equal(validNewPassword('short'),false)});
test('reset URL does not inherit hostile query and fragment or leak token into HTTP request',()=>{
  const token=generateResetToken();
  const u=new URL(resetLink('https://example.org/ignored?a=1#fragment',token));
  assert.equal(u.pathname,'/');
  assert.equal(u.search,'');
  assert.equal(new URLSearchParams(u.hash.slice(1)).get('reset_token'),token);
  assert.equal(u.origin+u.pathname+u.search,'https://example.org/');
  assert.ok(!u.pathname.includes(token) && !u.search.includes(token));
});
