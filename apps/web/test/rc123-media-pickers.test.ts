import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {mediaUploadMime} from '../src/widget-asset-upload.ts';

const root=new URL('../src/main.tsx',import.meta.url);
const editor=readFileSync(root,'utf8');

test('all presenter upload modes accept JPG when macOS file chooser omits MIME',()=>{
 for(const kind of ['logo','image','asset']){
  assert.equal(mediaUploadMime({name:'photo.JPEG',type:''},kind),'image/jpeg');
  assert.equal(mediaUploadMime({name:'photo.jpg',type:'application/octet-stream'},kind),'image/jpeg');
 }
 assert.equal(mediaUploadMime({name:'deck.pdf',type:''},'asset'),'application/pdf');
 assert.equal(mediaUploadMime({name:'clip.webm',type:''},'asset'),'video/webm');
 assert.equal(mediaUploadMime({name:'photo.jpg',type:''},'pdf'),null);
 assert.equal(mediaUploadMime({name:'deck.pdf',type:''},'logo'),null);
});

test('asset MIME fallback remains strict and never guesses an unapproved extension',()=>{
 for(const name of ['file.svg','file.exe','file.html','file.txt','file.jpg.exe']){
  for(const kind of ['asset','image','logo','video','pdf']){
   assert.equal(mediaUploadMime({name,type:''},kind),null,`${kind}: ${name}`);
  }
 }
 assert.equal(mediaUploadMime({name:'report.jpg',type:'text/html'},'logo'),null);
 assert.equal(mediaUploadMime({name:'report.JPG',type:'IMAGE/JPEG; charset=binary'},'logo'),'image/jpeg');
 assert.equal(mediaUploadMime({name:'report.jpg',type:'image/jpg'},'image'),'image/jpeg');
 assert.equal(mediaUploadMime({name:'report.jpg',type:'image/pjpeg'},'image'),'image/jpeg');
 assert.equal(mediaUploadMime({name:'report.jpg',type:'application/x-jpeg'},'image'),'image/jpeg');
});

test('all five presenter file-picker entry points use the same validated MIME resolution',()=>{
 const routes=['uploadAsset','uploadWidgetFillImage','uploadWidgetMedia','uploadBackground','importSlideImages'];
 for (const name of routes){
  const body=editor.slice(editor.indexOf(`async function ${name}(`));
  assert.ok(body.startsWith(`async function ${name}(`),name);
  assert.match(body.slice(0,1350),/mediaUploadMime\(file,\s*'(?:asset|image)'\)|mediaUploadMime\(file,kind\)/,name);
 }
 assert.match(editor,/headers:\{'Content-Type':mime\},body:file/g);
});
