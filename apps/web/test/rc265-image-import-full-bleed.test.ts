import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import {slideBackground,slideBackgroundCss} from '../src/master-background.ts';
import {validPageDesign} from '../../api/src/domain.ts';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const api=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');

for(const [fit,size] of [['cover','cover'],['contain','contain'],['fill','100% 100%']] as const){
 test(`RC265 imported page uses ${fit} image sizing without leaking scheme background`,()=>{
  const image=randomUUID(),themeImage=randomUUID();
  const page={backgroundAssetId:image,importedImageFit:fit,suppressMaster:true,backgroundColor:'#ffffff',widgets:[]};
  const theme={master:{backgroundAssetId:themeImage}};
  assert.equal(validPageDesign(page),true);
  assert.deepEqual(slideBackground(page,theme),{assetId:image});
  const style=slideBackgroundCss(page,theme,id=>`/session/image/${id}`);
  assert.equal(style.backgroundImage,`url("/session/image/${image}")`);
  assert.equal(style.backgroundSize,size);
  assert.equal(style.backgroundColor,'#ffffff');
  assert.equal(style.backgroundRepeat,'no-repeat');
  assert.ok(!JSON.stringify(style).includes(themeImage));
 });
}

test('RC265 rejects invalid modes and unsupported metadata before persistence',()=>{
 const base={backgroundAssetId:randomUUID(),widgets:[]};
 for(const value of ['overfill','none','url(https://evil)','',27,null])assert.equal(validPageDesign({...base,importedImageFit:value}),false);
 assert.equal(validPageDesign({importedImageFit:'cover'}),false);
 assert.equal(validPageDesign({...base,suppressMaster:'true'}),false);
 assert.equal(validPageDesign({...base,suppressMaster:true}),true);
});

test('RC265 import request transports validated full-bleed options into a single page background',()=>{
 assert.match(ui,/X-Quorivio-Image-Fit/);
 assert.match(ui,/X-Quorivio-Hide-Scheme/);
 assert.match(api,/invalid_import_image_options/);
 assert.match(api,/JSON\.stringify\(\{backgroundAssetId:assetId,backgroundColor:'#ffffff',importedImageFit,suppressMaster:suppressMaster==='1',widgets:\[\]\}\)/);
 assert.match(ui,/useState<'contain'\|'cover'\|'fill'>\('cover'\)/);
 assert.match(ui,/useState\(true\);const \[pageContextOpen/);
 assert.match(ui,/Espansione forzata/);
 assert.match(ui,/Nascondi schema, titoli, footer e numero pagina/);
});

test('RC265 suppresses inherited title/footer/number overlays on imported pages in all presentations',()=>{
 assert.match(ui,/activity\.page_design\?\.suppressMaster\?/);
 assert.match(ui,/audienceActivity\?\.page_design\?\.suppressMaster\?/);
 assert.match(ui,/entry\.activity\.page_design\?\.suppressMaster\?/);
 assert.match(ui,/numberingWidgets=\{\(snap\.activities\.find/);
 assert.match(ui,/!viewActivity\?\.page_design\?\.importedImageFit&&/);
 assert.match(ui,/!entry\.activity\.page_design\?\.importedImageFit&&/);
});

test('RC265 thumbnails render actual image pixels instead of text placeholder',()=>{
 assert.match(ui,/page-editor-preview-real-image/);
 assert.match(ui,/<ThumbnailWidgetContent widget=\{w\} assetUrl=\{w\.assetId\?\(assets\.find\(asset=>asset\.id===w\.assetId\)/);
 assert.match(ui,/data-imported-image=\{/);
 assert.match(ui,/!\(a as any\)\.page_design\?\.importedImageFit&&<span className="page-editor-preview-title"/);
 assert.match(css,/page-editor-preview\[data-imported-image="true"\]::after\{display:none!important;/);
 assert.match(css,/page-editor-preview-real-image\{/);
});

test('RC265 canvas size mode is carried through editor render and exported CSS',()=>{
 assert.match(ui,/--editor-page-background-size/);
 assert.match(css,/background-size:var\(--editor-page-background-size,cover\)!important/);
 assert.match(ui,/importedImageFit=\{\(snap\.activities\.find/);
});
