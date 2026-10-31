import test from 'node:test';
import assert from 'node:assert/strict';
import {widgetDisplay,newFooterWidget} from '../src/slide-master.ts';
import {rehearsalFreeTextRows} from '../src/widget-results.ts';

test('RC75: optional page number displays only as a positive integer',()=>{
 const footer=newFooterWidget('footer');
 assert.equal(widgetDisplay(footer,{sessionTitle:'Sessione'}).page,'');
 assert.equal(widgetDisplay(footer,{pageNumber:0}).page,'');
 assert.equal(widgetDisplay(footer,{pageNumber:1.5}).page,'');
 assert.equal(widgetDisplay(footer,{pageNumber:3}).page,'3');
 assert.equal(widgetDisplay({...footer,footerShowPageNumber:false},{pageNumber:3}).page,'');
});

test('RC75: preview free-text answer mode is scoped to selected subquestion',()=>{
 const source={id:'question-1',kind:'question',answerMode:'single',questions:[
  {id:'text-1',label:'Risposta',answerMode:'text'},
  {id:'choice-1',label:'Opzione',answerMode:'single'},
 ]};
 const answers={'question-1:text-1':'Un testo inserito dal partecipante',
   'question-1:choice-1':'a'};
 const textRows=rehearsalFreeTextRows(source,answers,'text-1');
 assert.equal(textRows.at(-1)?.label,'Un testo inserito dal partecipante');
 assert.deepEqual(rehearsalFreeTextRows(source,answers,'choice-1'),[]);
 assert.deepEqual(rehearsalFreeTextRows({id:'question-2',kind:'question',answerMode:'multiple'},{}),[]);
});
