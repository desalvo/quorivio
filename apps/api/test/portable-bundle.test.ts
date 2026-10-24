import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash,randomUUID} from 'node:crypto';
import {encodeBundle,decodeBundle,referencedAssets} from '../src/portable-bundle.ts';
const id=randomUUID();
const bytes=Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),Buffer.from('sample embedded binary media')]);
const definition={format:'quorivio-session',version:1,session:{theme:{}},activities:[{page_design:{backgroundAssetId:id,widgets:[{kind:'image',assetId:id}]},result_design:{}}]};
const manifest={format:'quorivio-bundle' as const,version:1 as const,definition,assets:[{id,mime:'image/png',bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')}]};
test('portable bundle roundtrips binary media and keeps references',()=>{
 const zip=encodeBundle(manifest,new Map([[id,bytes]]));const decoded=decodeBundle(zip);
 assert.deepEqual(decoded.manifest,manifest);assert.deepEqual(decoded.media.get(id),bytes);assert.deepEqual(referencedAssets(decoded.manifest.definition),new Set([id]));
});
test('portable bundle rejects tampering and truncated bytes',()=>{
 const zip=encodeBundle(manifest,new Map([[id,bytes]]));
 assert.throws(()=>decodeBundle(zip.subarray(0,zip.length-6)));
 const tampered=Buffer.from(zip);const ix=tampered.indexOf(Buffer.from('media/'));tampered[ix+2]=46;
 assert.throws(()=>decodeBundle(tampered));
 assert.throws(()=>encodeBundle({...manifest,assets:[{...manifest.assets[0],sha256:'a'.repeat(64)}]},new Map([[id,bytes]])));
});
test('portable bundle rejects missing asset even if it is referenced in a background',()=>{
 assert.throws(()=>encodeBundle({...manifest,assets:[]},new Map()));
});

// ZIP local headers and central directory must describe exactly the same bytes.
test('portable bundle rejects mismatched local metadata and overlapping payloads',()=>{
 const zip=encodeBundle(manifest,new Map([[id,bytes]]));
 const index=zip.lastIndexOf(Buffer.from([0x50,0x4b,0x05,0x06]));
 const central=zip.readUInt32LE(index+16);
 const localCrc=Buffer.from(zip);localCrc.writeUInt32LE(0,14);
 assert.throws(()=>decodeBundle(localCrc),/invalid_bundle_local/);
 const localFlags=Buffer.from(zip);localFlags.writeUInt16LE(8,6);
 assert.throws(()=>decodeBundle(localFlags),/invalid_bundle_local/);
 const localSizes=Buffer.from(zip);localSizes.writeUInt32LE(0,18);
 assert.throws(()=>decodeBundle(localSizes),/invalid_bundle_local/);
 const localExtra=Buffer.from(zip);localExtra.writeUInt16LE(1,28);
 assert.throws(()=>decodeBundle(localExtra),/invalid_bundle_payload/);
 // The second directory entry cannot point back into the first payload.
 const firstNameLength=zip.readUInt16LE(central+28);
 const secondCentral=central+46+firstNameLength;
 const overlapping=Buffer.from(zip);overlapping.writeUInt32LE(0,secondCentral+42);
 assert.throws(()=>decodeBundle(overlapping));
});

test('portable bundle rejects a valid digest for media with a deceptive MIME type',()=>{
 const fake=Buffer.from('not a PNG, despite a matching sha256');
 const bad={...manifest,assets:[{...manifest.assets[0],bytes:fake.length,sha256:createHash('sha256').update(fake).digest('hex')}]};
 assert.throws(()=>encodeBundle(bad,new Map([[id,fake]])),/bundle_asset_mismatch/);
});
