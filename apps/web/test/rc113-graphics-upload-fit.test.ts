import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {mediaUploadMime} from '../src/widget-asset-upload.ts';
import {freeWidgetPosition,overlapsOtherWidgets,rejectWidgetCollisions} from '../src/widget-placement.ts';
import {widgetAppearanceStyle,widgetShapeOutline} from '../src/widget-appearance.ts';
import {validPageDesign,validWidgetTextStyle} from '../../api/src/domain.ts';
const web=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const pos={x:12,y:12,width:50,height:50};
test('logo and backgrounds support JPEG selected by desktop OS file picker with empty MIME',()=>{
 assert.equal(mediaUploadMime({name:'photo.jpg',type:''},'logo'),'image/jpeg');
 assert.equal(mediaUploadMime({name:'photo.JPEG',type:''},'image'),'image/jpeg');
 assert.equal(mediaUploadMime({name:'photo.jpg',type:'application/octet-stream'},'logo'),'image/jpeg');
 assert.equal(mediaUploadMime({name:'movie.mp4',type:''},'video'),'video/mp4');
 assert.equal(mediaUploadMime({name:'not-png.html',type:''},'logo'),null);
 assert.match(web,/setAutoSaveBlockedSignature\(''\);setPageSaveError\(''\);await refreshAssets/);
 assert.match(web,/headers:\{'Content-Type':mime\},body:file/);
});
test('double click starts inline editing without auto-opening the inspector',()=>{
 assert.match(web,/onDoubleClick=\{e=>\{setActive\(w\.id\);setSelectedWidgets\(\[w\.id\]\);setContextWidget\(null\);/);
 assert.match(web,/Proprietà widget<\/button>/);
});
test('new shape and line are validated, old separator remains readable',()=>{
 for(const kind of ['shape','line','divider'])assert.equal(validPageDesign({widgets:[{id:'graphic01',kind,label:'Example',position:pos}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'g1',kind:'shape',showTitle:false,style:{shapeType:'star',strokeColor:'#334155',strokeWidth:2},position:pos}]}),true);
 assert.equal(validPageDesign({widgets:[{id:'g2',kind:'line',style:{lineDirection:'reverse',strokeDash:'dot',strokeWidth:0},position:pos}]}),true);
 assert.equal(validWidgetTextStyle({lineDirection:'unsafe'}),false);
 assert.equal(validPageDesign({widgets:[{id:'g2',kind:'line',showTitle:'no'}]}),false);
 assert.match(web,/editorWidgetKinds=\['rating','reactions','text','shape','line'/);
});
test('graphics can overlay functional widgets without collision relaxation between normal widgets',()=>{
 const normal={id:'a',kind:'question',position:pos};
 const other={id:'b',kind:'text',position:pos};
 const shape={id:'c',kind:'shape',position:pos};
 const line={id:'d',kind:'line',position:pos};
 assert.equal(overlapsOtherWidgets([normal,other],['b']),true);
 assert.equal(overlapsOtherWidgets([normal,shape,line],['c','d']),false);
 assert.equal(overlapsOtherWidgets([normal,shape,line],['a']),false);
 assert.deepEqual(rejectWidgetCollisions([normal],[normal,shape],['c']).map(x=>x.id),['a','c']);
 assert.ok(freeWidgetPosition([shape,line],{x:12,y:12},40,30));
});
test('star and heart outlines are true vector contours while default width zero has no line',()=>{
 assert.ok(widgetShapeOutline({shapeType:'star',strokeWidth:2,strokeColor:'#123456'})?.path.startsWith('M '));
 assert.ok(widgetShapeOutline({shapeType:'heart',strokeWidth:2,strokeColor:'#123456'})?.path);
 assert.equal(widgetShapeOutline({shapeType:'heart',strokeWidth:0}),null);
 assert.equal(widgetAppearanceStyle({strokeWidth:0}).borderStyle,'none');
});
test('overflow fits content in editor presenter and rehearsal, with visible editor rescale indicator',()=>{
 assert.equal(web.match(/<WidgetContentFit/g)?.length>=3,true);
 assert.match(web,/ResizeObserver\(measure\)/);
 assert.match(web,/MutationObserver\(measure\)/);
 assert.match(css,/\.widget-rescale-indicator/);
 assert.match(web,/Mostra nome\/titolo del widget/);
});
