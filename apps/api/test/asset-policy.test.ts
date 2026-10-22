import test from 'node:test';import assert from 'node:assert/strict';import {sniffAsset,validAsset} from '../src/asset-policy.ts';
test('reject scripts and mismatched declared MIME',()=>{const evil=Buffer.from('<svg onload=alert(1)>');assert.equal(sniffAsset(evil),null);assert.equal(validAsset(evil,'image/png',100),false)});
test('recognize PDF magic and enforce maximum bytes',()=>{const pdf=Buffer.from('%PDF-1.7\n1234567890');assert.equal(sniffAsset(pdf),'application/pdf');assert.equal(validAsset(pdf,'application/pdf',100),true);assert.equal(validAsset(pdf,'image/png',100),false);assert.equal(validAsset(pdf,'application/pdf',10),false)});
test('reject unsupported document format',()=>{assert.equal(sniffAsset(Buffer.from('PK\x03\x04xxxxxxxxxxxx')),null)});
