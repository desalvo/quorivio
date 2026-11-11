import test from 'node:test';
import assert from 'node:assert/strict';
import {gaugeModel} from '../src/widget-results.ts';

test('RC314 Gauge accepts comma and dot decimal statistical scores',()=>{
 const rows=[{id:'a',label:'7,5',count:2},{id:'b',label:'8.5',count:1},{id:'c',label:'9',count:0}];
 const model=gaugeModel(rows,{},'question');
 assert.ok(model.value!==null);
 assert.ok(Math.abs(model.value-47/6)<1e-9);
 assert.equal(model.min,0);
 assert.equal(model.max,8.5);
 assert.equal(model.total,3);
 assert.equal(gaugeModel(rows,{gaugeAggregation:'min'}).value,7.5);
 assert.equal(gaugeModel(rows,{gaugeAggregation:'max'}).value,8.5);
});

test('RC314 Gauge never coerces blank or hexadecimal category labels to scores',()=>{
 assert.equal(gaugeModel([{id:'a',label:' ',count:3}]).value,3);
 const rows=[{id:'a',label:'0x10',count:2},{id:'b',label:'2',count:8}];
 assert.equal(gaugeModel(rows).value,5);
 assert.equal(gaugeModel(rows,{gaugeAggregation:'max'}).value,8);
});
