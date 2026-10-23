import test from 'node:test';
import assert from 'node:assert/strict';
import {createEmailOtp,validEmailOtp,emailOtpDigest,matchesEmailOtp} from '../src/email-otp.ts';
const secret='a'.repeat(40);
test('email OTP codes are six-digit strings, including leading zeroes',()=>{for(let i=0;i<100;i++)assert.match(createEmailOtp(),/^\d{6}$/);assert.equal(validEmailOtp(123456),false);assert.equal(validEmailOtp('12345'),false);assert.equal(validEmailOtp('123456'),true)});
test('OTP HMAC is challenge/user scoped and timing-safe checked',()=>{const d=emailOtpDigest('000001','user1','challenge1',secret);assert.equal(matchesEmailOtp('000001',d,'user1','challenge1',secret),true);assert.equal(matchesEmailOtp('000001',d,'user2','challenge1',secret),false);assert.equal(matchesEmailOtp('000001',d,'user1','challenge2',secret),false);assert.equal(matchesEmailOtp('000002',d,'user1','challenge1',secret),false);assert.equal(matchesEmailOtp('000001','invalid','user1','challenge1',secret),false)});
test('reject short secret and malformed OTP',()=>{assert.throws(()=>emailOtpDigest('111111','u','c','short'));assert.throws(()=>emailOtpDigest('wrong','u','c',secret))});
