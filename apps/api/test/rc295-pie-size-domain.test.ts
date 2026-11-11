import test from 'node:test';
import assert from 'node:assert/strict';
import {validPageDesign,publicPageDesign} from '../src/domain.ts';

const widget={id:'results-1',kind:'results-button',label:'Risultati',resultsView:'pie',pieShowPercentages:true};

test('persist pie sizes 25 through 150 without changing the result source',()=>{
 for(const pieSize of [25,40,50,72,85,100,125,150]){
  const design={widgets:[{...widget,pieSize}]};
  assert.equal(validPageDesign(design),true,String(pieSize));
  assert.equal(publicPageDesign(design as any)?.widgets?.[0].pieSize,pieSize);
 }
});
test('legacy result widgets without pie size remain valid',()=>{
 assert.equal(validPageDesign({widgets:[widget]}),true);
});
test('reject unsafe, out-of-range, fractional and unrelated widget pie sizes',()=>{
 for(const pieSize of [-1,0,20,24,25.1,150.1,151,Infinity,NaN,'75',null]){
  assert.equal(validPageDesign({widgets:[{...widget,pieSize}]}),false,String(pieSize));
 }
 assert.equal(validPageDesign({widgets:[{id:'text-1',kind:'text',label:'Hello',pieSize:75}]}),false);
});

test('QR image size persists independently of widget size',()=>{
 const qr={id:'qr-1',kind:'qr',qrImagePixels:140,position:{x:2,y:2,width:25,height:20}};
 assert.equal(validPageDesign({widgets:[qr]}),true);
 assert.equal(publicPageDesign({widgets:[qr]} as any)?.widgets?.[0].qrImagePixels,140);
 for(const qrImagePixels of [0,15,4097,Infinity,NaN])assert.equal(validPageDesign({widgets:[{...qr,qrImagePixels}]}),false);
});
