import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {moveWidgetsToCollisionLimit,resizeWidgetToCollisionLimit,freeWidgetPosition,rejectWidgetCollisions} from '../src/widget-placement.ts';
import {aggregateShortTextAnswers} from '../../api/src/widget-revisions.ts';
import {rowsFromWidgetAnswerDetail} from '../src/widget-results.ts';
import {validPageDesign} from '../../api/src/domain.ts';
const main=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const w=(id:string,x:number,y:number,width:number,height:number)=>({id,kind:'results-button',position:{x,y,width,height},autoFit:true});
test('RC138: moving a result layer onto another widget is permitted and saved',()=>{
 const base=[w('results',10,10,20,20),w('question',50,10,20,20)];
 const moved=moveWidgetsToCollisionLimit(base,['results'],40,0);
 assert.equal(moved[0].position.x,50);
 assert.deepEqual(rejectWidgetCollisions(base,moved,['results']),moved);
 assert.deepEqual(freeWidgetPosition(base,{x:50,y:10},20,20),{x:50,y:10,width:20,height:20});
 assert.equal(validPageDesign({widgets:[{id:'results',kind:'results-button',position:moved[0].position},{id:'question',kind:'question',position:moved[1].position}]}),true);
});
test('RC138: shrinking lower edge disables auto fit rather than rescaling the result chart',()=>{
 const original=[w('results',10,10,35,40)];
 const next=resizeWidgetToCollisionLimit(original,'results',{x:10,y:10,width:35,height:14});
 assert.equal(next[0].position.height,14);
 assert.equal(next[0].autoFit,false);
 assert.equal(original[0].position.height,40);
 assert.match(main,/aria-label="Ridimensionamento automatico contenuto risultati"/);
 assert.match(main,/allowScale=\{w.kind!=='results-button'\|\|w.autoFit!==false\}/);
 assert.match(css,/widget-fit-frame\[data-fit-mode="scroll"\] \.linked-results/);
});
test('RC138: presenter-owned results are aggregate only and never include answer identity',()=>{
 const rows=[
  {answer_mode:'text',answer_payload:{text:'Machine Learning'}},
  {answer_mode:'text',answer_payload:{text:'machine   learning'}},
  {answer_mode:'text',answer_payload:{text:'A third long text that is not a two-word answer'}},
 ];
 const groups=aggregateShortTextAnswers(rows);
 assert.deepEqual(groups,[{word:'machine learning',count:2}]);
 const chart=rowsFromWidgetAnswerDetail({id:'q',kind:'question',answerMode:'text'} as any,{revisions:[{texts:3}],text_counts:groups});
 assert.deepEqual(chart,[{id:'text:machine learning',label:'machine learning',count:2}]);
 assert.match(main,/<PresenterLinkedResult sessionId=\{sessionId\}/);
 assert.match(main,/<LinkedResultChart widget=\{w\} widgets=\{widgets\}/);
});
