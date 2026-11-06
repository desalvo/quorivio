import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizedFileName,numberedFileName,findAvailableFileName} from '../src/file-display-names.ts';

test('uploads keep recognizable filenames but never use a path',()=>{
 assert.equal(normalizedFileName('slides/Comunicazione 2026.pdf','X'),'Comunicazione 2026.pdf');
 assert.equal(normalizedFileName('C:\\Users\\Test\\Logo ufficiale.PNG','X'),'Logo ufficiale.PNG');
 assert.equal(normalizedFileName('\u0000','fallback'),'fallback');
});
test('numbered duplicates keep the extension, including multibyte names',()=>{
 assert.equal(numberedFileName('Foto.jpg',2),'Foto (2).jpg');
 assert.equal(numberedFileName('sfondo',3),'sfondo (3)');
 assert.equal(numberedFileName('report.PDF',10),'report (10).PDF');
 assert.ok(numberedFileName('x'.repeat(150)+'.png',2).length<=120);
});
test('never overwrite an existing filename or skip numbered collisions',async()=>{
 const existing=new Set(['foto.png','foto (2).png']);
 assert.deepEqual(await findAvailableFileName('foto.png',async n=>existing.has(n.toLowerCase())),{duplicate:true,name:'foto (3).png'});
 assert.deepEqual(await findAvailableFileName('originale.jpg',async n=>existing.has(n.toLowerCase())),{duplicate:false,name:'originale.jpg'});
});
