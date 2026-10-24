import {createWriteStream} from 'node:fs';
import {mkdir,open,unlink} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {once} from 'node:events';
// Independent header sniffing keeps the streaming receiver dependency-free.
function sniffAsset(data:Buffer):string|null{
 if(data.length<12)return null;
 if(data.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))return 'image/png';
 if(data[0]===255&&data[1]===216&&data[2]===255)return 'image/jpeg';
 if(['GIF87a','GIF89a'].includes(data.toString('ascii',0,6)))return 'image/gif';
 if(data.toString('ascii',0,4)==='RIFF'&&data.toString('ascii',8,12)==='WEBP')return 'image/webp';
 if(data.toString('ascii',0,5)==='%PDF-')return 'application/pdf';
 if(data.subarray(0,4).equals(Buffer.from([0x50,0x4b,0x03,0x04])))return 'application/vnd.openxmlformats-officedocument.presentationml.presentation';
 if(data.toString('ascii',4,8)==='ftyp')return 'video/mp4';
 if(data.subarray(0,4).equals(Buffer.from([0x1a,0x45,0xdf,0xa3])))return 'video/webm';
 return null;
}

/** Stream a bounded raw upload to a private temporary file and atomically rename it.
 * Never buffers full user-controlled media in application memory. */
export async function receiveAssetStream(source:AsyncIterable<Uint8Array>,folder:string,id:string,declared:string,limit:number,expected:number){
 if(!Number.isSafeInteger(expected)||expected<1||expected>limit)throw Error('invalid_upload_size');
 await mkdir(folder,{recursive:true,mode:0o700});
 const temporary=path.join(folder,`.${id}.upload`);
 const destination=path.join(folder,id);
 const hash=createHash('sha256');let received=0;let prefix=Buffer.alloc(0);
 const stream=createWriteStream(temporary,{flags:'wx',mode:0o600});
 try{
  for await(const data of source){
   const chunk=Buffer.from(data);received+=chunk.length;
   if(received>limit||received>expected)throw Error('upload_too_large');
   if(prefix.length<32)prefix=Buffer.concat([prefix,chunk.subarray(0,32-prefix.length)]);
   hash.update(chunk);
   if(!stream.write(chunk))await once(stream,'drain');
  }
  if(received!==expected)throw Error('upload_length_mismatch');
  if(sniffAsset(prefix)!==declared&&!(declared==='application/vnd.quorivio.session+zip'&&sniffAsset(prefix)==='application/vnd.openxmlformats-officedocument.presentationml.presentation'))throw Error('invalid_media_signature');
  stream.end();await once(stream,'finish');
  // Exclusive destination creation prevents overwriting previously uploaded media.
  const target=await open(destination,'wx',0o600);await target.close();
  try{const {rename}=await import('node:fs/promises');await rename(temporary,destination)}catch(e){await unlink(destination).catch(()=>{});throw e}
  return {size:received,sha256:hash.digest('hex'),destination};
 }catch(e){stream.destroy();if(!stream.closed)await once(stream,'close').catch(()=>{});await unlink(temporary).catch(()=>{});throw e}
}
