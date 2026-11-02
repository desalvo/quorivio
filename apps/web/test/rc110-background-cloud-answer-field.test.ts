import test from 'node:test';
import assert from 'node:assert/strict';
import {cloudRankColor,CLOUD_REMAINDER_COLOR,rankCloudItems} from '../src/word-cloud-rank.ts';
import {answerInputStyle} from '../src/widget-answer-style.ts';
import {validWidgetTextStyle,validPageDesign} from '../../api/src/domain.ts';

test('word clouds rank by frequency, color only the first five independently, then use one uniform color',()=>{
 const words=[{word:'zeta',count:1},{word:'top',count:9},{word:'alpha',count:1},{word:'second',count:8},{word:'third',count:7},{word:'fourth',count:6},{word:'fifth',count:5},{word:'other',count:2}];
 const ranked=rankCloudItems(words,w=>w.count,w=>w.word);
 assert.deepEqual(ranked.map(w=>w.word),['top','second','third','fourth','fifth','other','alpha','zeta']);
 assert.deepEqual(words[0],{word:'zeta',count:1},'source data must not be mutated');
 assert.equal(new Set(Array.from({length:5},(_,i)=>cloudRankColor(i))).size,5);
 assert.ok(Array.from({length:5},(_,i)=>cloudRankColor(i)).every(c=>c!==CLOUD_REMAINDER_COLOR));
 assert.equal(cloudRankColor(5),CLOUD_REMAINDER_COLOR);
 assert.equal(cloudRankColor(100),CLOUD_REMAINDER_COLOR);
 assert.equal(cloudRankColor(-1),CLOUD_REMAINDER_COLOR);
});

test('free-text entry width and height apply without changing submit button',()=>{
 const fields=answerInputStyle({answerFieldWidth:65,answerFieldHeight:180,answerColor:'#224466',answerFontSize:21});
 assert.equal(fields.width,'65%');assert.equal(fields.height,'14.06250cqw');assert.equal(fields.color,'#224466');
 assert.equal(answerInputStyle({}).width,'100%');assert.equal(answerInputStyle({}).height,'7.50000cqw');
});

test('API rejects out-of-bounds response field sizes, noninteger values and CSS payloads',()=>{
 const valid={answerFieldWidth:25,answerFieldHeight:48};
 assert.equal(validWidgetTextStyle(valid),true);
 assert.equal(validWidgetTextStyle({answerFieldWidth:100,answerFieldHeight:400}),true);
 for(const invalid of [0,24,101,34.5,Infinity,NaN,'100%'])assert.equal(validWidgetTextStyle({answerFieldWidth:invalid}),false);
 for(const invalid of [0,47,401,99.5,Infinity,NaN,'expression()'])assert.equal(validWidgetTextStyle({answerFieldHeight:invalid}),false);
 const widget={id:'w1',kind:'question',label:'Testo libero',answerMode:'text',style:{answerFieldWidth:75,answerFieldHeight:160}};
 assert.equal(validPageDesign({widgets:[widget]}),true);
 assert.equal(validPageDesign({widgets:[{...widget,style:{answerFieldHeight:900}}]}),false);
});
