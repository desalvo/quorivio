import {createHash,randomUUID} from 'node:crypto';
import {deflateRawSync,inflateRawSync} from 'node:zlib';
// Keep the archive parser dependency-free for both Node's source tests and compiled API builds.
function sniffAsset(data:Buffer):string|null{
 if(data.length<12)return null;
 if(data.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))return 'image/png';
 if(data[0]===255&&data[1]===216&&data[2]===255)return 'image/jpeg';
 if(['GIF87a','GIF89a'].includes(data.toString('ascii',0,6)))return 'image/gif';
 if(data.toString('ascii',0,4)==='RIFF'&&data.toString('ascii',8,12)==='WEBP')return 'image/webp';
 if(data.toString('ascii',0,5)==='%PDF-')return 'application/pdf';
 if(data.toString('ascii',4,8)==='ftyp')return 'video/mp4';
 if(data.subarray(0,4).equals(Buffer.from([0x1a,0x45,0xdf,0xa3])))return 'video/webm';
 return null;
}

export const BUNDLE_MIME='application/vnd.quorivio.session+zip';
export const MAX_BUNDLE_BYTES=100*1024*1024;
export const MAX_MEDIA_BYTES=80*1024*1024;
const encoder=new TextEncoder();
const UUID_RE=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const MAX_MANIFEST_BYTES=2*1024*1024;
const CRC_TABLE=Array.from({length:256},(_,i)=>{let c=i;for(let j=0;j<8;j++)c=c&1?0xedb88320^(c>>>1):c>>>1;return c>>>0});
export function crc32(data:Uint8Array){let c=0xffffffff;for(const b of data)c=CRC_TABLE[(c^b)&255]^(c>>>8);return (c^0xffffffff)>>>0}
export type BundleAsset={id:string;mime:string;bytes:number;sha256:string};
export type BundleManifest={format:'quorivio-bundle';version:1;definition:any;assets:BundleAsset[]};
export function referencedAssets(definition:any):Set<string>{
 const out=new Set<string>();const add=(v:any)=>{if(typeof v==='string'&&v)out.add(v)};
 const scan=(x:any)=>{if(!x||typeof x!=='object')return;add(x.backgroundAssetId);if(Array.isArray(x.widgets))for(const w of x.widgets)if(['image','logo','video','pdf'].includes(w?.kind))add(w.assetId)};
 scan(definition?.session?.theme);for(const a of definition?.activities||[]){scan(a.page_design);scan(a.result_design)}return out;
}
/** Give every imported asset a fresh instance-global ID, preserving shared references
 * across session theme, page layouts and result layouts. Never mutate caller input. */
export function remapPortableAssets(definition:any,sourceAssetIds:string[]):{definition:any;ids:Map<string,string>}{
 const source=new Set(sourceAssetIds);
 if(source.size!==sourceAssetIds.length||sourceAssetIds.some(id=>typeof id!=='string'||!UUID_RE.test(id)))throw Error('invalid_import_assets');
 const refs=referencedAssets(definition);
 if(refs.size!==source.size||[...refs].some(id=>!source.has(id)))throw Error('unmatched_import_assets');
 const ids=new Map(sourceAssetIds.map(id=>[id,randomUUID()]));
 const copy=structuredClone(definition);
 const rewrite=(design:any)=>{
  if(!design||typeof design!=='object')return;
  if(typeof design.backgroundAssetId==='string')design.backgroundAssetId=ids.get(design.backgroundAssetId);
  if(Array.isArray(design.widgets))for(const widget of design.widgets){
   if(['image','logo','video','pdf'].includes(widget?.kind)&&typeof widget.assetId==='string')widget.assetId=ids.get(widget.assetId);
  }
 };
 rewrite(copy.session?.theme);
 if(Array.isArray(copy.activities))for(const activity of copy.activities){rewrite(activity.page_design);rewrite(activity.result_design)}
 return {definition:copy,ids};
}
export function validateBundleManifest(m:any):m is BundleManifest{
 if(!m||m.format!=='quorivio-bundle'||m.version!==1||!m.definition||!Array.isArray(m.assets)||m.assets.length>300)return false;
 const ids=new Set<string>();let total=0;
 for(const a of m.assets){if(!a||typeof a.id!=='string'||!UUID_RE.test(a.id)||ids.has(a.id)||!['image/png','image/jpeg','image/gif','image/webp','application/pdf','video/mp4','video/webm'].includes(a.mime)||!Number.isSafeInteger(a.bytes)||a.bytes<1||a.bytes>50*1024*1024||! /^[a-f0-9]{64}$/.test(a.sha256))return false;ids.add(a.id);total+=a.bytes;}
 if(total>MAX_MEDIA_BYTES)return false;
 const refs=referencedAssets(m.definition);return refs.size===ids.size&&[...refs].every(id=>ids.has(id));
}
const write16=(b:Buffer,o:number,n:number)=>b.writeUInt16LE(n,o),write32=(b:Buffer,o:number,n:number)=>b.writeUInt32LE(n>>>0,o);
export function encodeBundle(manifest:BundleManifest,media:Map<string,Buffer>):Buffer{
 if(!validateBundleManifest(manifest))throw Error('invalid_bundle_manifest');
 const manifestBody=Buffer.from(JSON.stringify(manifest));
 if(manifestBody.length>MAX_MANIFEST_BYTES)throw Error('invalid_bundle_manifest_size');
 const entries:[string,Buffer][]=[['manifest.json',manifestBody]];
 for(const a of manifest.assets){const buf=media.get(a.id);if(!buf||buf.length!==a.bytes||sniffAsset(buf)!==a.mime||createHash('sha256').update(buf).digest('hex')!==a.sha256)throw Error('bundle_asset_mismatch');entries.push([`media/${a.id}`,buf]);}
 let cursor=0;const chunks:Buffer[]=[],directory:Buffer[]=[];
 for(const [name,body] of entries){const file=Buffer.from(encoder.encode(name)),compressed=deflateRawSync(body,{level:6});const checksum=crc32(body);const hdr=Buffer.alloc(30);write32(hdr,0,0x04034b50);write16(hdr,4,20);write16(hdr,8,8);write32(hdr,14,checksum);write32(hdr,18,compressed.length);write32(hdr,22,body.length);write16(hdr,26,file.length);chunks.push(hdr,file,compressed);const cd=Buffer.alloc(46);write32(cd,0,0x02014b50);write16(cd,4,20);write16(cd,6,20);write16(cd,10,8);write32(cd,16,checksum);write32(cd,20,compressed.length);write32(cd,24,body.length);write16(cd,28,file.length);write32(cd,42,cursor);directory.push(cd,file);cursor+=hdr.length+file.length+compressed.length;}
 const dirSize=directory.reduce((s,b)=>s+b.length,0);if(cursor+dirSize+22>MAX_BUNDLE_BYTES)throw Error('invalid_bundle_size');const end=Buffer.alloc(22);write32(end,0,0x06054b50);write16(end,8,entries.length);write16(end,10,entries.length);write32(end,12,dirSize);write32(end,16,cursor);return Buffer.concat([...chunks,...directory,end]);
}
export function decodeBundle(archive:Buffer):{manifest:BundleManifest;media:Map<string,Buffer>}{
 if(archive.length>MAX_BUNDLE_BYTES||archive.length<22)throw Error('invalid_bundle_size');
 const end=archive.length-22;if(archive.readUInt32LE(end)!==0x06054b50||archive.readUInt16LE(end+20)!==0||archive.readUInt16LE(end+4)!==0||archive.readUInt16LE(end+6)!==0)throw Error('invalid_bundle_zip');
 const count=archive.readUInt16LE(end+10),directorySize=archive.readUInt32LE(end+12),start=archive.readUInt32LE(end+16);if(count<1||count>301||count!==archive.readUInt16LE(end+8)||start+directorySize!==end)throw Error('invalid_bundle_directory');
 let offset=start,total=0,declaredTotal=0;const files=new Map<string,Buffer>();const ranges:[number,number][]=[];
 for(let i=0;i<count;i++){
  if(offset+46>end||archive.readUInt32LE(offset)!==0x02014b50)throw Error('invalid_bundle_entry');
  const flags=archive.readUInt16LE(offset+8),method=archive.readUInt16LE(offset+10),crc=archive.readUInt32LE(offset+16),compressedSize=archive.readUInt32LE(offset+20),size=archive.readUInt32LE(offset+24),nameSize=archive.readUInt16LE(offset+28),extra=archive.readUInt16LE(offset+30),comment=archive.readUInt16LE(offset+32),localOffset=archive.readUInt32LE(offset+42);
  if(flags!==0||![0,8].includes(method)||extra||comment||size>50*1024*1024||compressedSize>MAX_BUNDLE_BYTES||offset+46+nameSize>end||localOffset+30>start)throw Error('unsafe_bundle_entry');
  const name=archive.subarray(offset+46,offset+46+nameSize).toString('utf8');if(!/^(manifest\.json|media\/[0-9a-f-]{36})$/.test(name)||files.has(name))throw Error('unsafe_bundle_path');
  if(name==='manifest.json'&&size>MAX_MANIFEST_BYTES)throw Error('invalid_bundle_manifest_size');
  // Bound aggregate declared sizes before inflating any following entry.
  declaredTotal+=size;if(declaredTotal>MAX_MEDIA_BYTES+MAX_MANIFEST_BYTES)throw Error('bundle_exceeds_quota');
  if(archive.readUInt32LE(localOffset)!==0x04034b50||archive.readUInt16LE(localOffset+6)!==flags||archive.readUInt16LE(localOffset+8)!==method||archive.readUInt32LE(localOffset+14)!==crc||archive.readUInt32LE(localOffset+18)!==compressedSize||archive.readUInt32LE(localOffset+22)!==size)throw Error('invalid_bundle_local');
  const localNameSize=archive.readUInt16LE(localOffset+26),localExtra=archive.readUInt16LE(localOffset+28),dataOffset=localOffset+30+localNameSize+localExtra;
  if(localExtra!==0||localNameSize!==nameSize||dataOffset+compressedSize>start||archive.subarray(localOffset+30,localOffset+30+localNameSize).toString('utf8')!==name)throw Error('invalid_bundle_payload');
  ranges.push([localOffset,dataOffset+compressedSize]);
  const compressed=archive.subarray(dataOffset,dataOffset+compressedSize);const body=method===8?inflateRawSync(compressed,{maxOutputLength:size+1}):Buffer.from(compressed);
  if(body.length!==size||crc32(body)!==crc)throw Error('bundle_checksum_mismatch');total+=body.length;if(total>MAX_MEDIA_BYTES+2*1024*1024)throw Error('bundle_exceeds_quota');files.set(name,body);offset+=46+nameSize+extra+comment;
 }
 ranges.sort((a,b)=>a[0]-b[0]);let covered=0;for(const [begin,finish] of ranges){if(begin!==covered||finish<=begin)throw Error('invalid_bundle_layout');covered=finish;}if(covered!==start)throw Error('invalid_bundle_layout');
 if(offset!==end||!files.has('manifest.json')||files.get('manifest.json')!.length>2*1024*1024)throw Error('invalid_bundle_manifest');
 let manifest:BundleManifest;try{manifest=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(files.get('manifest.json')!))}catch{throw Error('invalid_bundle_manifest_json')}
 if(!validateBundleManifest(manifest)||files.size!==manifest.assets.length+1)throw Error('invalid_bundle_manifest');
 const media=new Map<string,Buffer>();for(const a of manifest.assets){const body=files.get(`media/${a.id}`);if(!body||body.length!==a.bytes||sniffAsset(body)!==a.mime||createHash('sha256').update(body).digest('hex')!==a.sha256)throw Error('bundle_asset_mismatch');media.set(a.id,body)}
 return {manifest,media};
}
