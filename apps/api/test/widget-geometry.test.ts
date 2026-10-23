import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {validWidgetPosition} from '../src/domain.ts';
test('slide widgets permit bounded width and height',()=>{
 assert.equal(validWidgetPosition({x:12,y:20,width:50,height:30}),true);
 assert.equal(validWidgetPosition({x:12,y:20,width:50}),true); // previous layout remains valid
});
test('slide widget bounds reject overflowing or malformed size',()=>{
 for(const p of [{x:10,y:80,width:50,height:30},{x:75,y:2,width:40,height:15},{x:5,y:5,width:30,height:-1},{x:5,y:5,width:30,height:Infinity},{x:2,y:2,width:20,height:0}]) assert.equal(validWidgetPosition(p),false);
});
