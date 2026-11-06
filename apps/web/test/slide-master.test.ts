import assert from 'node:assert/strict';
import test from 'node:test';
import {newTitleWidget,newFooterWidget,widgetDisplay,slidePageNumber,DEFAULT_TITLE_STYLE,footerPageNumber} from '../src/slide-master.ts';
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
 assert.equal(f.kind,'footer');assert.equal(f.position?.width,100);assert.equal(f.position?.y,93);assert.equal(f.position?.height,7);
 assert.equal(f.style?.fillNone,true);
 assert.deepEqual(widgetDisplay(f,{sessionTitle:'Quorivio session',pageNumber:3}).center,'Quorivio session');
 assert.deepEqual(widgetDisplay(f,{sessionTitle:'Quorivio session',pageNumber:3}).page,'3');
 assert.equal(slidePageNumber([{id:'c'},{id:'a'},{id:'b'}],'a'),2);
 assert.equal(widgetDisplay({...f,footerShowSessionTitle:false,footerShowPageNumber:false,label:'Copyright'},{sessionTitle:'Quorivio session',pageNumber:5}).center,'Copyright');
 assert.equal(widgetDisplay({...f,footerShowSessionTitle:false,footerShowPageNumber:false,label:'Copyright'},{sessionTitle:'Quorivio session',pageNumber:5}).page,'');
});

test('default master fonts are readable on a white slide and explicit widget styles win over stale theme defaults',()=>{
 assert.equal(DEFAULT_TITLE_STYLE.color,'#000000');
 const scheme=newTitleWidget('Default');
 scheme.style={...scheme.style,color:'#143658',fontSize:46};
 const result=widgetDisplay(scheme,{masterTitleStyle:{color:'#fefefe',fontSize:90},pageTitle:'Edited'});
 assert.equal(result.style.color,'#143658');assert.equal(result.style.fontSize,46);
 assert.equal(result.title,'Edited');
});
test('numbering overlay is derived from the footer presence, not footer geometry',()=>{
 const footer={...newFooterWidget('foot'),position:{x:30,y:30,width:20,height:20,rotation:43},style:{color:'#092f42',fontSize:22}};
 const number=footerPageNumber([footer],7);
 assert.deepEqual(number,{text:'7',fontFamily:'Arial',fontSize:22,color:'#092f42',bold:false,italic:false,underline:false,strikethrough:false,paddingRight:5,paddingBottom:5});
 assert.equal(footerPageNumber([footer],0),null);
 assert.equal(footerPageNumber([{...footer,footerShowPageNumber:false}],5),null);
 assert.equal(footerPageNumber([],5),null);
 assert.equal(slidePageNumber([{id:'a'}],'removed'),0);
});

test('footer numbering can be independently hidden and repositioned in footer space',()=>{
 const f=newFooterWidget('foot');
 const custom={...f,footerNumberX:50,footerNumberY:45};
 const number=footerPageNumber([custom],9)!;
 assert.equal(number.text,'9');
 assert.equal(number.x,50);
 assert.ok(Math.abs(number.y-96.15)<1e-5);
 assert.equal(footerPageNumber([{...custom,footerShowPageNumber:false}],9),null);
});


test('RC142: footer page number style and right/bottom padding are independently configurable',()=>{
 const f=newFooterWidget('foot');
 const custom={...f,style:{...f.style,fontSize:24,color:'#111111',footerNumberFontFamily:'Georgia',footerNumberFontSize:18,footerNumberColor:'#ff6600',footerNumberPaddingRight:2,footerNumberPaddingBottom:7}};
 const num=footerPageNumber([custom],3)!;
 assert.equal(num.fontFamily,'Georgia');assert.equal(num.fontSize,18);assert.equal(num.color,'#ff6600');
 assert.equal(num.paddingRight,2);assert.equal(num.paddingBottom,7);
});
