import test from 'node:test';
import assert from 'node:assert/strict';
import {safeWidgetFontFamily,explicitWidgetFontFamily,initialWidgetTextStyle,widgetTextDefaults,WIDGET_FONT_FAMILIES} from '../src/widget-typography-defaults.ts';
import {widgetTypographyStyle} from '../src/widget-appearance.ts';
import {answerInputStyle,answerOptionStyle,answerSubmitStyle} from '../src/widget-answer-style.ts';
import {inlineMarkCss,inlineMarkDomCss,styledSegments} from '../src/widget-text-marks.ts';
import {resultTextCss} from '../src/result-text-style.ts';
import {newTitleWidget,newFooterWidget,footerPageNumber} from '../src/slide-master.ts';
import {validWidgetTextStyle,validWidgetInlineMarks} from '../../api/src/domain.ts';

const kinds=['title','footer','question','timed-quiz','topic-question','rating','reactions','timer','qr','profile','text','postit','participant-count','results-button','shape','line','image','video','logo','pdf'];
const fields=['label','description','option:one','question:sub:label','question:sub:description','question:sub:option:one'];

test('RC254: every new canvas and schema widget kind uses Arial; all unmarked rich fields inherit',()=>{
 for(const kind of kinds){
  const initial=initialWidgetTextStyle(kind);
  assert.equal(widgetTypographyStyle(widgetTextDefaults(kind,initial)).fontFamily,'Arial',kind);
  for(const field of fields){
   const segments=styledSegments('Text in new '+kind,[],field);
   assert.equal(segments.length,1);
   assert.equal(inlineMarkCss(segments[0].style).fontFamily,undefined,kind+':'+field);
   assert.equal(inlineMarkDomCss(segments[0].style).fontFamily,undefined,kind+':'+field);
  }
 }
 assert.equal(widgetTypographyStyle(newTitleWidget('Page').style).fontFamily,'Arial');
 assert.equal(widgetTypographyStyle(newFooterWidget('f').style).fontFamily,'Arial');
 assert.equal(footerPageNumber([newFooterWidget('f')],3)?.fontFamily,'Arial');
});

test('RC254: literal undefined, null, empty and invalid font values cannot become CSS font names',()=>{
 const invalid=[undefined,null,'','  ','undefined','null','NaN','[object Object]',false,1];
 for(const value of invalid){
  assert.equal(safeWidgetFontFamily(value),'Arial',String(value));
  assert.equal(explicitWidgetFontFamily(value),undefined,String(value));
  const malformed={fontFamily:value as string,answerFontFamily:value as string,submitFontFamily:value as string,footerNumberFontFamily:value as string};
  assert.equal(widgetTypographyStyle(malformed).fontFamily,'Arial');
  assert.equal(answerOptionStyle(malformed).fontFamily,'Arial');
  assert.equal(answerOptionStyle(malformed)['--q-answer-font-family'],'Arial');
  assert.equal(answerInputStyle(malformed).fontFamily,'Arial');
  assert.equal(answerSubmitStyle(malformed).fontFamily,'Arial');
  assert.equal(inlineMarkCss({fontFamily:value as string}).fontFamily,undefined);
  assert.equal(inlineMarkDomCss({fontFamily:value as string}).fontFamily,undefined);
  assert.equal(resultTextCss({sourceTitle:{fontFamily:value as string}},'sourceTitle').fontFamily,undefined);
  assert.equal(footerPageNumber([{...newFooterWidget('f'),style:malformed}],1)?.fontFamily,'Arial');
 }
 assert.equal(validWidgetTextStyle({fontFamily:'undefined'}),false);
 assert.equal(validWidgetInlineMarks([{field:'label',start:0,end:2,style:{fontFamily:'undefined'}}]),false);
});

test('RC254: explicit widget, answer, footer and per-character fonts remain independent',()=>{
 for(const family of WIDGET_FONT_FAMILIES){
  const style={fontFamily:family,answerFontFamily:'Tahoma',submitFontFamily:'Verdana',footerNumberFontFamily:'Georgia'};
  assert.equal(widgetTypographyStyle(style).fontFamily,family);
  assert.equal(answerOptionStyle(style).fontFamily,'Tahoma');
  assert.equal(answerSubmitStyle(style).fontFamily,'Verdana');
  assert.equal(footerPageNumber([{...newFooterWidget('f'),style}],1)?.fontFamily,'Georgia');
  assert.equal(inlineMarkDomCss({fontFamily:family}).fontFamily,family);
  assert.equal(inlineMarkDomCss({fontFamily:'Trebuchet MS'}).fontFamily,'Trebuchet MS');
 }
});
