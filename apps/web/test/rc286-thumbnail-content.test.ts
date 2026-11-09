import test from 'node:test';
import assert from 'node:assert/strict';
import {thumbnailWidgetModel} from '../src/thumbnail-widget-content.ts';

test('authored choice widget thumbnail has actual question and all visible option captions',()=>{
 const m=thumbnailWidgetModel({kind:'question',label:'Quale risposta?',answerMode:'multiple',options:[{label:'Verde'},{label:'Rosso'},{label:'Blu'}]});
 assert.equal(m.type,'choice');assert.equal(m.label,'Quale risposta?');assert.deepEqual(m.options,['Verde','Rosso','Blu']);assert.equal(m.multi,true);
});
test('independent subquestion captions are used if root has no options',()=>{
 const m=thumbnailWidgetModel({kind:'question',questions:[{label:'Seconda domanda',answerMode:'single',options:[{label:'Prima'}]}]});
 assert.equal(m.type,'choice');assert.deepEqual(m.options,['Prima']);
});
test('chart preview never invents live response counts',()=>{
 const m=thumbnailWidgetModel({kind:'results-button',label:'Risultati test'});
 assert.equal(m.type,'chart');assert.deepEqual(m.options,[]);assert.ok(!JSON.stringify(m).includes('42'));
});
test('timer, media, rating, QR, shapes and standard text retain their type',()=>{
 assert.equal(thumbnailWidgetModel({kind:'timer',durationSeconds:92}).timer,'1:32');
 assert.equal(thumbnailWidgetModel({kind:'image',assetId:'x'}).isImage,true);
 assert.equal(thumbnailWidgetModel({kind:'rating'}).type,'rating');
 assert.equal(thumbnailWidgetModel({kind:'qrcode'}).type,'qr');
 assert.equal(thumbnailWidgetModel({kind:'line'}).type,'line');
 assert.equal(thumbnailWidgetModel({kind:'title',label:'Prologo'}).label,'Prologo');
});
