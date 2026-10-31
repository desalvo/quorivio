import test from 'node:test';
import assert from 'node:assert/strict';
import {allowedSameHostBrowserOrigin,qrBrowserOrigin} from '../src/origin-policy.ts';
test('authenticated browser QR can use its actual same-origin ingress address',()=>{
 const canonical='http://localhost:8080';
 assert.equal(qrBrowserOrigin(canonical,'https://quorivio.example.net/dashboard','quorivio.example.net','same-origin'),'https://quorivio.example.net');
 assert.equal(qrBrowserOrigin(canonical,'https://evil.example.net/dashboard','quorivio.example.net','same-origin'),canonical);
 assert.equal(qrBrowserOrigin(canonical,'https://quorivio.example.net/dashboard','quorivio.example.net','cross-site'),canonical);
 assert.equal(qrBrowserOrigin(canonical,'https://quorivio.example.net/dashboard','quorivio.example.net',undefined),canonical);
});
test('websocket same-host exemption rejects foreign origins and userinfo',()=>{
 assert.equal(allowedSameHostBrowserOrigin('https://quorivio.example.net','quorivio.example.net'),true);
 assert.equal(allowedSameHostBrowserOrigin('https://evil.net','quorivio.example.net'),false);
 assert.equal(allowedSameHostBrowserOrigin('https://evil.net@quorivio.example.net','quorivio.example.net'),false);
 assert.equal(allowedSameHostBrowserOrigin('javascript://quorivio.example.net','quorivio.example.net'),false);
 assert.equal(allowedSameHostBrowserOrigin('https://quorivio.example.net/path','quorivio.example.net'),false);
});
