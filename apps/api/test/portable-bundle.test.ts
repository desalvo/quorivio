import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash,randomUUID} from 'node:crypto';
import {encodeBundle,decodeBundle,referencedAssets,remapPortableAssets} from '../src/portable-bundle.ts';
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


test('portable import remaps every theme, page and result reference consistently without mutating the source',()=>{
 const other=randomUUID();
 const source={...definition,session:{theme:{backgroundAssetId:id,widgets:[{id:'picture',kind:'logo',assetId:other}]}},activities:[
  {page_design:{backgroundAssetId:other,widgets:[{id:'one',kind:'image',assetId:id},{id:'two',kind:'video',assetId:other}]},result_design:{backgroundAssetId:id,widgets:[{id:'three',kind:'pdf',assetId:other}]}}
 ]};
 const untouched=structuredClone(source);
 const first=remapPortableAssets(source,[id,other]);
 const second=remapPortableAssets(source,[id,other]);
 assert.deepEqual(source,untouched);
 assert.equal(first.ids.size,2);
 assert.notEqual(first.ids.get(id),id);
 assert.notEqual(first.ids.get(id),second.ids.get(id));
 assert.notEqual(first.ids.get(id),first.ids.get(other));
 assert.deepEqual(referencedAssets(first.definition),new Set(first.ids.values()));
 assert.equal(first.definition.session.theme.backgroundAssetId,first.ids.get(id));
 assert.equal(first.definition.activities[0].page_design.widgets[0].assetId,first.ids.get(id));
 assert.equal(first.definition.activities[0].result_design.backgroundAssetId,first.ids.get(id));
 assert.equal(first.definition.activities[0].result_design.widgets[0].assetId,first.ids.get(other));
 assert.throws(()=>remapPortableAssets(source,[id]),/unmatched_import_assets/);
 assert.throws(()=>remapPortableAssets(source,[id,other,other]),/invalid_import_assets/);
 assert.throws(()=>remapPortableAssets(source,[id,other,'../secret']),/invalid_import_assets/);
});

test('portable bundle can be independently imported twice with fresh UUID assignments',()=>{
 const zip=encodeBundle(manifest,new Map([[id,bytes]]));
 const a=remapPortableAssets(decodeBundle(zip).manifest.definition,[id]);
 const b=remapPortableAssets(decodeBundle(zip).manifest.definition,[id]);
 assert.notEqual(a.ids.get(id),b.ids.get(id));
 assert.equal(a.definition.activities[0].page_design.backgroundAssetId,a.ids.get(id));
 assert.equal(b.definition.activities[0].page_design.widgets[0].assetId,b.ids.get(id));
});


test('portable bundle rejects non-canonical malformed UUIDs before export and remapping',()=>{
 const badId='12345678-1234-1234-1234-123456789abc-';
 const badDefinition={...definition,activities:[{page_design:{backgroundAssetId:badId},result_design:{}}]};
 const badManifest={...manifest,definition:badDefinition,assets:[{...manifest.assets[0],id:badId}]};
 assert.throws(()=>encodeBundle(badManifest,new Map([[badId,bytes]])),/invalid_bundle_manifest/);
 assert.throws(()=>remapPortableAssets(badDefinition,[badId]),/invalid_import_assets/);
});

test('portable bundle refuses manifests above the 2 MiB bound before compression',()=>{
 const huge={...manifest,definition:{...definition,description:'x'.repeat(2*1024*1024)}};
 assert.throws(()=>encodeBundle(huge,new Map([[id,bytes]])),/invalid_bundle_manifest_size/);
});

test('portable bundle rejects inflated manifest size declared by ZIP directory before decompression',()=>{
 const zip=Buffer.from(encodeBundle(manifest,new Map([[id,bytes]])));
 const end=zip.length-22;const central=zip.readUInt32LE(end+16);
 zip.writeUInt32LE(3*1024*1024,central+24);
 assert.throws(()=>decodeBundle(zip),/invalid_bundle_manifest_size/);
});


test('portable export rejects archive size exceeding the maximum even for valid media',()=>{
 const huge=Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),Buffer.alloc(45*1024*1024)]);
 const a=randomUUID(),b=randomUUID();
 const media=new Map([[a,huge],[b,huge]]);
 const d={format:'quorivio-session',version:1,session:{theme:{}},activities:[{page_design:{widgets:[{kind:'image',assetId:a},{kind:'image',assetId:b}]}}]};
 const m={...manifest,definition:d,assets:[a,b].map(id=>({id,mime:'image/png',bytes:huge.length,sha256:createHash('sha256').update(huge).digest('hex')}))};
 assert.throws(()=>encodeBundle(m,media),/invalid_bundle_manifest/); // aggregate media quota
});

test('portable bundle rejects aggregate declared ZIP size before media inflation',()=>{
 const zip=Buffer.from(encodeBundle(manifest,new Map([[id,bytes]])));
 const end=zip.length-22,central=zip.readUInt32LE(end+16);
 zip.writeUInt32LE(84*1024*1024,central+24);
 assert.throws(()=>decodeBundle(zip),/unsafe_bundle_entry/);
});
