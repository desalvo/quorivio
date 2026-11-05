import assert from 'node:assert/strict';
import test from 'node:test';
import {DEFAULT_TITLE_STYLE,DEFAULT_FOOTER_STYLE,newTitleWidget,newFooterWidget,widgetDisplay,footerPageNumber} from '../src/slide-master.ts';
import {widgetTypographyStyle} from '../src/widget-appearance.ts';
import {stageWidgetTypography} from '../src/stage-widget-typography.ts';
import {widgetTextDefaults} from '../src/widget-typography-defaults.ts';

test('default title/footer Arial is resolved from shared source not an editor string',()=>{
 assert.equal(DEFAULT_TITLE_STYLE.fontFamily,'Arial');
 assert.equal(DEFAULT_FOOTER_STYLE.fontFamily,'Arial');
 assert.equal(widgetDisplay(newTitleWidget('Test'),{pageTitle:'Test'}).style.fontFamily,'Arial');
 assert.equal(newFooterWidget('f').style?.fontFamily,'Arial');
 assert.equal(footerPageNumber([newFooterWidget('f')],1)?.fontFamily,'Arial');
 assert.equal(widgetTypographyStyle(undefined).fontFamily,'Arial');
});

test('master and per-widget overrides are preserved in editor and stage',()=>{
 const widget=newTitleWidget('Title');
 const context={pageTitle:'Other',masterTitleStyle:{fontFamily:'Georgia',fontSize:31}};
 assert.equal(widgetDisplay(widget,context).style.fontFamily,'Georgia');
 assert.equal(stageWidgetTypography(widget,context).fontFamily,'Georgia');
 assert.equal(stageWidgetTypography(widget,context,true).fontFamily,'Georgia');
 const custom={...widget,style:{...widget.style,fontFamily:'Verdana',fontSize:34}};
 assert.equal(widgetDisplay(custom,context).style.fontFamily,'Verdana');
 assert.equal(stageWidgetTypography(custom,context).fontFamily,'Verdana');
 assert.equal(stageWidgetTypography(custom,context,true).fontFamily,'Verdana');
 const footer=newFooterWidget('footer');
 const customized={...footer,style:{...footer.style,fontFamily:'Tahoma',footerNumberFontFamily:'Georgia'}};
 assert.equal(footerPageNumber([customized],2)?.fontFamily,'Georgia');
 assert.equal(widgetTypographyStyle(customized.style).fontFamily,'Tahoma');
});

test('question defaults resolve independently without overwriting authored typefaces',()=>{
 const empty=widgetTextDefaults('question',{});
 assert.equal(empty?.fontFamily,'Arial');
 assert.equal(empty?.answerFontFamily,'Arial');
 assert.equal(empty?.bold,true);
 const authored={fontFamily:'Verdana',answerFontFamily:'Georgia',bold:false};
 const resolved=widgetTextDefaults('question',authored);
 assert.equal(resolved?.fontFamily,'Verdana');
 assert.equal(resolved?.answerFontFamily,'Georgia');
 assert.equal(resolved?.bold,false);
 assert.deepEqual(authored,{fontFamily:'Verdana',answerFontFamily:'Georgia',bold:false});
});
