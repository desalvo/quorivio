import {test} from 'node:test';
import assert from 'node:assert/strict';
import {inspectProfileImage,MAX_PROFILE_IMAGE_SIDE,MAX_PROFILE_IMAGE_PIXELS} from '../src/profile-image.ts';
function png(w=96,h=96){const b=Buffer.alloc(40);Buffer.from([137,80,78,71,13,10,26,10]).copy(b);b.writeUInt32BE(13,8);b.write('IHDR',12);b.writeUInt32BE(w,16);b.writeUInt32BE(h,20);b[24]=8;b[25]=6;return b}
function jpeg(w=96,h=96){return Buffer.from([255,216,255,224,0,4,0,0,255,192,0,11,8,h>>8,h&255,w>>8,w&255,3,1,0,2,0,0,0,0,0])}
function webpX(w=96,h=96){const b=Buffer.alloc(30);b.write('RIFF',0);b.writeUInt32LE(22,4);b.write('WEBP',8);b.write('VP8X',12);b.writeUInt32LE(10,16);b.writeUIntLE(w-1,24,3);b.writeUIntLE(h-1,27,3);return b}
function webpL(w=96,h=96){const b=Buffer.alloc(30);b.write('RIFF',0);b.writeUInt32LE(22,4);b.write('WEBP',8);b.write('VP8L',12);b.writeUInt32LE(5,16);b[20]=0x2f;b[21]=(w-1)&255;b[22]=(((w-1)>>8)&63)|(((h-1)&3)<<6);b[23]=((h-1)>>2)&255;b[24]=((h-1)>>10)&15;return b}
function webpV(w=96,h=96){const b=Buffer.alloc(30);b.write('RIFF',0);b.writeUInt32LE(22,4);b.write('WEBP',8);b.write('VP8 ',12);b.writeUInt32LE(10,16);b[23]=0x9d;b[24]=1;b[25]=0x2a;b.writeUInt16LE(w,26);b.writeUInt16LE(h,28);return b}
const good:[string,Buffer,number,number][]=[
 ['PNG square',png(),96,96],['PNG portrait',png(500,900),500,900],['PNG landscape',png(900,500),900,500],
 ['JPEG square',jpeg(),96,96],['JPEG portrait',jpeg(200,400),200,400],['JPEG landscape',jpeg(400,200),400,200],
 ['WebP extended square',webpX(),96,96],['WebP extended portrait',webpX(200,400),200,400],['WebP extended landscape',webpX(400,200),400,200],
 ['WebP lossless square',webpL(),96,96],['WebP lossless portrait',webpL(200,400),200,400],['WebP lossless landscape',webpL(400,200),400,200],
 ['WebP lossy square',webpV(),96,96],['WebP lossy portrait',webpV(200,400),200,400],['WebP lossy landscape',webpV(400,200),400,200],
 ['PNG one pixel',png(1,1),1,1],['JPEG one pixel',jpeg(1,1),1,1],['WebP one pixel',webpX(1,1),1,1],
 ['PNG maximum side',png(MAX_PROFILE_IMAGE_SIDE,1),MAX_PROFILE_IMAGE_SIDE,1],
 ['JPEG maximum side',jpeg(MAX_PROFILE_IMAGE_SIDE,1),MAX_PROFILE_IMAGE_SIDE,1],
 ['WebP maximum side',webpX(MAX_PROFILE_IMAGE_SIDE,1),MAX_PROFILE_IMAGE_SIDE,1]
];
for(const [name,b,w,h] of good)test('profile photo accepts '+name,()=>{const mime=name.startsWith('PNG')?'image/png':name.startsWith('JPEG')?'image/jpeg':'image/webp';assert.deepEqual(inspectProfileImage(b,mime),{mime,width:w,height:h})});
const invalid:[string,Buffer,string][]=[
 ['PNG width zero',png(0,96),'image/png'],['PNG height zero',png(96,0),'image/png'],
 ['PNG excessive width',png(4097,96),'image/png'],['PNG excessive height',png(96,4097),'image/png'],
 ['PNG excessive pixels',png(4096,4096),'image/png'],
 ['PNG invalid IHDR length',(()=>{const b=png();b.writeUInt32BE(12,8);return b})(),'image/png'],
 ['PNG invalid IHDR type',(()=>{const b=png();b.write('JHDR',12);return b})(),'image/png'],
 ['PNG invalid compression',(()=>{const b=png();b[26]=1;return b})(),'image/png'],
 ['PNG invalid filter',(()=>{const b=png();b[27]=1;return b})(),'image/png'],
 ['PNG invalid interlace',(()=>{const b=png();b[28]=2;return b})(),'image/png'],
 ['PNG invalid color',(()=>{const b=png();b[25]=5;return b})(),'image/png'],
 ['JPEG zero width',jpeg(0,96),'image/jpeg'],['JPEG zero height',jpeg(96,0),'image/jpeg'],
 ['JPEG excessive width',jpeg(4097,96),'image/jpeg'],['JPEG excessive pixels',jpeg(4096,4096),'image/jpeg'],
 ['JPEG missing SOF',Buffer.from([255,216,255,224,0,4,0,0,255,217,...Array(20).fill(0)]),'image/jpeg'],
 ['JPEG corrupt segment size',(()=>{const b=jpeg();b[4]=0;b[5]=1;return b})(),'image/jpeg'],
 ['JPEG wrong magic',(()=>{const b=jpeg();b[0]=0;return b})(),'image/jpeg'],
 ['WebP RIFF wrong size',(()=>{const b=webpX();b.writeUInt32LE(123,4);return b})(),'image/webp'],
 ['WebP invalid chunk',(()=>{const b=webpX();b.write('XXXX',12);return b})(),'image/webp'],
 ['WebP invalid width',webpX(4097,1),'image/webp'],
 ['WebP invalid height',webpL(1,4097),'image/webp'],
 ['WebP invalid pixel count',webpV(4096,4096),'image/webp'],
 ['WebP missing lossy marker',(()=>{const b=webpV();b[23]=0;return b})(),'image/webp'],
 ['WebP missing lossless marker',(()=>{const b=webpL();b[20]=0;return b})(),'image/webp'],
 ['WebP invalid signature',(()=>{const b=webpX();b.write('BAD!',8);return b})(),'image/webp'],
 ['PNG mislabeled JPEG',png(),'image/jpeg'],['JPEG mislabeled WebP',jpeg(),'image/webp'],
 ['WebP mislabeled PNG',webpX(),'image/png'],['unsupported SVG',Buffer.from('<svg>'.padEnd(30,' ')),'image/svg+xml'],
 ['empty upload',Buffer.alloc(0),'image/png'],['tiny upload',Buffer.alloc(23),'image/png'],
 ['over limit',Buffer.alloc(5*1024*1024+1),'image/png']
];
for(const [name,b,mime] of invalid)test('profile photo rejects '+name,()=>assert.throws(()=>inspectProfileImage(b,mime),/invalid_profile_image/));
test('profile pixel limit is explicit',()=>assert.equal(MAX_PROFILE_IMAGE_PIXELS,16_000_000));
import {readFileSync} from 'node:fs';
for(const [extension,mime] of [['png','image/png'],['jpg','image/jpeg'],['webp','image/webp']] as const){
 test('profile photo accepts real encoded '+extension+' fixture',()=>{
  const bytes=readFileSync(new URL(`./fixtures/profile-valid.${extension}`,import.meta.url));
  assert.deepEqual(inspectProfileImage(bytes,mime),{mime,width:19,height:13});
 });
}
