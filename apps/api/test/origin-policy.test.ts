import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {allowedWriteOrigin,allowedLiveOrigin} from '../src/origin-policy.ts';

test('rejects cross-scheme Origin even if host matches',()=>{
 assert.equal(allowedWriteOrigin('http://example.org','https://example.org'),false);
 assert.equal(allowedWriteOrigin('https://example.org','https://example.org'),true);
});
test('rejects cross-port, deceptive origin and invalid URL',()=>{
 assert.equal(allowedWriteOrigin('https://example.org:8443','https://example.org'),false);
 assert.equal(allowedWriteOrigin('https://example.org.evil.test','https://example.org'),false);
 assert.equal(allowedWriteOrigin('oops','https://example.org'),false);
 assert.equal(allowedWriteOrigin(undefined,'https://example.org'),true);
});
test('websocket origin rejects cross-scheme and cross-port origins',()=>{
 assert.equal(allowedLiveOrigin('https://example.org','https://example.org'),true);
 assert.equal(allowedLiveOrigin('http://example.org','https://example.org'),false);
 assert.equal(allowedLiveOrigin('https://example.org:8443','https://example.org'),false);
 assert.equal(allowedLiveOrigin('https://example.org.evil.test','https://example.org'),false);
});
