import test from 'node:test';
import assert from 'node:assert/strict';
import {inlineMarkCss,inlineMarkDomCss,styledSegments} from '../src/widget-text-marks.ts';
import {initialWidgetTextStyle,widgetTextDefaults} from '../src/widget-typography-defaults.ts';

test('RC252: default widget question title and answer inherit Arial when marks are absent',()=>{
 for(const kind of ['question','timed-quiz','topic-question']){
  const style=initialWidgetTextStyle(kind);
  assert.equal(style.fontFamily,'Arial');
  assert.equal(widgetTextDefaults(kind,style)?.answerFontFamily,'Arial');
  for(const field of ['label','option:first','question:sub:label','question:sub:option:first']){
   const parts=styledSegments('Nuovo contenuto',[],field);
   assert.equal(parts.length,1);
   assert.deepEqual(inlineMarkDomCss(parts[0].style),{},field);
  }
 }
});

test('RC252: DOM serializer never writes literal undefined into any CSS property',()=>{
 assert.equal(inlineMarkCss({}).fontFamily,undefined,'React can ignore absent styles');
 const dom=inlineMarkDomCss({});
 assert.equal(Object.keys(dom).length,0);
 assert.ok(!Object.values(dom).includes('undefined'));
 assert.deepEqual(inlineMarkDomCss({bold:false,italic:false,underline:false}),{
  fontWeight:'normal',fontStyle:'normal',textDecoration:'none'
 });
});

test('RC252: author-specified inline Arial/Georgia and size remain untouched',()=>{
 const style={fontFamily:'Georgia',fontSize:22,bold:true,color:'#004488'} as const;
 const result=inlineMarkDomCss(style);
 assert.equal(result.fontFamily,'Georgia');
 assert.equal(result.fontSize,'1.71875cqw');
 assert.equal(result['--q-inline-phone-font-size'],'22px');
 assert.equal(result.fontWeight,'bold');
 assert.equal(result.color,'#004488');
 assert.ok(!Object.values(result).some(value=>String(value)==='undefined'));
});

test('RC252: custom base face and answer face stay independent',()=>{
 const style=widgetTextDefaults('question',{fontFamily:'Verdana',answerFontFamily:'Tahoma'});
 assert.equal(style?.fontFamily,'Verdana');
 assert.equal(style?.answerFontFamily,'Tahoma');
 assert.deepEqual(inlineMarkDomCss({fontFamily:'Arial'}),{fontFamily:'Arial'});
});
