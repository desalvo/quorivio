import test from 'node:test';
import assert from 'node:assert/strict';
import {resultTextCss} from '../src/result-text-style.ts';
import {applyAllWidgetTypeface} from '../src/widget-text-marks.ts';
import {GLOBAL_ZOOM_BASE,GLOBAL_ZOOM_CSS_VARIABLE,zoomStyleValue} from '../src/global-page-zoom.ts';

test('RC247 font dimensions are proportional to the 1280 stage, not editor pixels',()=>{
 const s=resultTextCss({'row:a':{fontFamily:'Arial',fontSize:32,color:'#008000'}},'row:a');
 assert.equal(s.fontSize,'2.50000cqw');
 assert.equal(s.fontFamily,'Arial');
 assert.equal(s.color,'#008000');
});
test('RC247 font face set on Widget intero reaches nested subquestions and inline answer spans',()=>{
 const original={style:{fontFamily:'Arial',answerFontFamily:'Verdana'},
  textMarks:[{field:'option:a',start:0,end:1,style:{fontFamily:'Georgia'}},
             {field:'question:one:option:a',start:0,end:1,style:{fontFamily:'Tahoma'}}]};
 const formatted=applyAllWidgetTypeface(original,{fontFamily:'Arial'});
 assert.equal(formatted.style.answerFontFamily,'Arial');
 assert.equal(formatted.style.submitFontFamily,'Arial');
 assert.equal(formatted.style.footerNumberFontFamily,'Arial');
 assert.equal(formatted.textMarks[0].style.fontFamily,'Arial');
 assert.equal(formatted.textMarks[1].style.fontFamily,'Arial');
 assert.equal(original.textMarks[1].style.fontFamily,'Tahoma');
});
test('RC247 interface 100 percent is old 80, with zoom screen compensation enabled',()=>{
 assert.equal(GLOBAL_ZOOM_BASE,0.8);
 assert.equal(GLOBAL_ZOOM_CSS_VARIABLE,'--quorivio-ui-scale');
 assert.equal(zoomStyleValue(100),'80%');
 assert.equal(zoomStyleValue(80),'64%');
 assert.equal(zoomStyleValue(120),'96%');
});
