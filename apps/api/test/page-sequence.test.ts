import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageOrder} from '../src/page-sequence.ts';
const a='11111111-1111-4111-8111-111111111111';
const b='22222222-2222-4222-8222-222222222222';
test('complete reorder is valid',()=>assert.equal(validPageOrder([b,a],[a,b]),true));
test('reject missing pages',()=>assert.equal(validPageOrder([a],[a,b]),false));
test('reject duplicate pages',()=>assert.equal(validPageOrder([a,a],[a,b]),false));
test('reject cross-session id',()=>assert.equal(validPageOrder([a,'33333333-3333-4333-8333-333333333333'],[a,b]),false));
test('empty session may remain empty',()=>assert.equal(validPageOrder([],[]),true));

test('reject malformed UUID even if present in existing page set',()=>assert.equal(validPageOrder(['11111111-1111-1111-1111-111111111111'],['11111111-1111-1111-1111-111111111111']),false));
test('reject duplicate existing page ids',()=>assert.equal(validPageOrder([a,a],[a,a]),false));
test('reject non-string ids',()=>assert.equal(validPageOrder([a,42],[a,b]),false));
