import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {productionCspDirectives,quorivioPermissionsPolicy} from '../src/security-headers.ts';

test('production CSP forbids inline scripts, remote scripts, eval and plugins',()=>{
 const c=productionCspDirectives('https://quorivio.example.org');
 assert.deepEqual(c.scriptSrc,["'self'"]);
 assert.deepEqual(c.scriptSrcAttr,["'none'"]);
 assert.deepEqual(c.objectSrc,["'none'"]);
 assert.deepEqual(c.baseUri,["'none'"]);
 assert.deepEqual(c.frameAncestors,["'self'"]);
 assert.deepEqual(c.formAction,["'self'"]);
 assert.deepEqual(c.connectSrc,["'self'",'wss://quorivio.example.org']);
 assert.ok(Object.hasOwn(c,'upgradeInsecureRequests'));
 assert.ok(!JSON.stringify(c).includes('unsafe-eval'));
});
test('subpath and explicit port keep WS connectivity scoped to browser origin',()=>{
 const c=productionCspDirectives('https://quorivio.example.org:8443/app');
 assert.deepEqual(c.connectSrc,["'self'",'wss://quorivio.example.org:8443']);
 const local=productionCspDirectives('http://localhost:8080');
 assert.deepEqual(local.connectSrc,["'self'",'ws://localhost:8080']);
 assert.ok(!Object.hasOwn(local,'upgradeInsecureRequests'));
});
test('widget media, QR, inline geometry and same-site presenter iframe survive policy',()=>{
 const c=productionCspDirectives('https://quorivio.example.org');
 assert.ok(c.styleSrc.includes("'unsafe-inline'"));
 assert.ok(c.imgSrc.includes('data:'));
 assert.ok(c.imgSrc.includes('blob:'));
 assert.ok(c.imgSrc.includes('https:'));
 assert.ok(c.mediaSrc.includes('blob:'));
 assert.ok(c.frameSrc.includes("'self'"));
 assert.ok(c.frameSrc.includes('https:'));
 assert.deepEqual(c.workerSrc,["'self'",'blob:']);
});
test('invalid public origin cannot silently weaken CSP WebSocket scope',()=>{
 for(const url of ['ftp://example.org','https://user:pass@example.org','https://example.org/?next=1','https://example.org/#x','invalid'])
  assert.throws(()=>productionCspDirectives(url));
});
test('unused powerful APIs are disabled, fullscreen remains available',()=>{
 for(const feature of ['camera=()','microphone=()','geolocation=()','payment=()','usb=()'])
  assert.ok(quorivioPermissionsPolicy.includes(feature));
 assert.ok(!quorivioPermissionsPolicy.includes('fullscreen'));
});
