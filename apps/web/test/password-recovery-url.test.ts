import assert from 'node:assert/strict';
import {test} from 'node:test';
import {consumeRecoveryTokenFromUrl} from '../src/password-recovery-url.ts';

function fixture(href:string) {
  const calls: Array<{state:unknown;url:string}> = [];
  const history = {
    state: {navigation: 7},
    replaceState(state:unknown, unused:string, url?:string|null){
      calls.push({state,url:String(url)});
    },
  };
  return {token:consumeRecoveryTokenFromUrl({href}, history),calls};
}

test('consumes the opaque reset bearer without putting it in browser history',()=>{
  const secret='TestRecoveryOpaqueSecretNeverStoreOrLog';
  const result=fixture('https://quorivio.invalid/?reset_token='+secret+'&lang=it#login');
  assert.equal(result.token,secret);
  assert.deepEqual(result.calls,[{state:{navigation:7},url:'/?lang=it#login'}]);
  assert.doesNotMatch(JSON.stringify(result.calls),/TestRecoveryOpaqueSecret/);
});

test('no recovery token leaves browser history untouched',()=>{
  assert.deepEqual(fixture('https://quorivio.invalid/?lang=it'),{token:'',calls:[]});
});

test('empty and duplicate token params are removed atomically',()=>{
  const empty=fixture('https://quorivio.invalid/?reset_token=&lang=en');
  assert.equal(empty.token,'');
  assert.deepEqual(empty.calls[0].url,'/?lang=en');
  const duplicate=fixture('https://quorivio.invalid/?reset_token=first&reset_token=second#recovery');
  assert.equal(duplicate.token,'first');
  assert.equal(duplicate.calls[0].url,'/#recovery');
});

test('preserves unicode and encoded nonsecret query values',()=>{
  const result=fixture('https://quorivio.invalid/join?subject=caff%C3%A8&reset_token=t%2B%3D&mode=1');
  assert.equal(result.token,'t+=');
  assert.equal(result.calls[0].url,'/join?subject=caff%C3%A8&mode=1');
});


test('fragment-based reset bearer never appears in request path or query and is removed from history',()=>{
  const token='fragment-recovery-secret-fixture';
  const result=fixture(`https://quorivio.invalid/?lang=fr#reset_token=${token}`);
  assert.equal(result.token,token);
  assert.deepEqual(result.calls,[{state:{navigation:7},url:'/?lang=fr'}]);
  assert.doesNotMatch(JSON.stringify(result.calls),/fragment-recovery-secret/);
});

test('both legacy query and new fragment bearers are removed, preferring the fragment',()=>{
  const result=fixture('https://quorivio.invalid/?reset_token=legacy&lang=it#reset_token=fragment');
  assert.equal(result.token,'fragment');
  assert.equal(result.calls[0].url,'/?lang=it');
  assert.doesNotMatch(JSON.stringify(result.calls),/legacy|fragment/);
});

test('fragment parser preserves unrelated fragment parameters without persisting the bearer',()=>{
  const result=fixture('https://quorivio.invalid/?lang=en#reset_token=a%2Bb%3D&view=presenter');
  assert.equal(result.token,'a+b=');
  assert.equal(result.calls[0].url,'/?lang=en#view=presenter');
  assert.deepEqual(fixture('https://quorivio.invalid/?lang=en#section'),{token:'',calls:[]});
});
