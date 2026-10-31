import assert from 'node:assert/strict';
import test from 'node:test';
import {newTitleWidget,newFooterWidget,widgetDisplay,slidePageNumber,DEFAULT_TITLE_STYLE} from '../src/slide-master.ts';
test('new slide has one central bold title bound to the mutable page name',()=>{
 const w=newTitleWidget('Prima pagina');
 assert.equal(w.kind,'title');assert.deepEqual(w.position,{x:8,y:3,width:84,height:12,rotation:0});
 assert.equal(widgetDisplay(w,{pageTitle:'Titolo rinominato'}).title,'Titolo rinominato');
 assert.equal(widgetDisplay(w,{pageTitle:'Titolo rinominato'}).style.bold,true);
 assert.equal(widgetDisplay(w,{pageTitle:'Titolo rinominato'}).style.textAlign,'center');
 assert.ok((DEFAULT_TITLE_STYLE.fontSize||0)>20);
});
test('slide master controls all inherited titles while overrides remain local',()=>{
 const w=newTitleWidget('Slide');
 assert.equal(widgetDisplay(w,{pageTitle:'Slide',masterTitleStyle:{fontSize:52,color:'#123456',fontFamily:'Georgia'}}).style.fontSize,52);
 assert.equal(widgetDisplay({...w,titleFollowPage:false,titleUseMaster:false,label:'Manuale',style:{fontSize:29,color:'#abcdef'}},{pageTitle:'Altro',masterTitleStyle:{fontSize:55}}).title,'Manuale');
 assert.equal(widgetDisplay({...w,titleFollowPage:false,titleUseMaster:false,label:'Manuale',style:{fontSize:29,color:'#abcdef'}},{pageTitle:'Altro',masterTitleStyle:{fontSize:55}}).style.fontSize,29);
});
test('footer is transparent full width at bottom, and page numbering follows current ordering',()=>{
 const f=newFooterWidget('footer-1');
 assert.equal(f.kind,'footer');assert.equal(f.position?.width,100);assert.equal(f.position?.y,94);assert.equal(f.position?.height,6);
 assert.equal(f.style?.fillNone,true);
 assert.deepEqual(widgetDisplay(f,{sessionTitle:'Quorivio session',pageNumber:3}).center,'Quorivio session');
 assert.deepEqual(widgetDisplay(f,{sessionTitle:'Quorivio session',pageNumber:3}).page,'3');
 assert.equal(slidePageNumber([{id:'c'},{id:'a'},{id:'b'}],'a'),2);
 assert.equal(widgetDisplay({...f,footerShowSessionTitle:false,footerShowPageNumber:false,label:'Copyright'},{sessionTitle:'Quorivio session',pageNumber:5}).center,'Copyright');
 assert.equal(widgetDisplay({...f,footerShowSessionTitle:false,footerShowPageNumber:false,label:'Copyright'},{sessionTitle:'Quorivio session',pageNumber:5}).page,'');
});
