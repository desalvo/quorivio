/** Bounded metadata validation for server-hosted profile images.  This does not
 * decode pixels or replace malware scanning: it rejects malformed headers and
 * decompression-bomb dimensions before an image is made publicly accessible. */
export type ProfileImageInfo={mime:'image/png'|'image/jpeg'|'image/webp';width:number;height:number};
export const MAX_PROFILE_IMAGE_SIDE=4096;
export const MAX_PROFILE_IMAGE_PIXELS=16_000_000;
const validDimensions=(width:number,height:number)=>Number.isSafeInteger(width)&&Number.isSafeInteger(height)&&width>0&&height>0&&width<=MAX_PROFILE_IMAGE_SIDE&&height<=MAX_PROFILE_IMAGE_SIDE&&width*height<=MAX_PROFILE_IMAGE_PIXELS;
const invalid=():never=>{throw Error('invalid_profile_image')};
export function inspectProfileImage(bytes:Uint8Array,declared:string):ProfileImageInfo{
 const b=Buffer.from(bytes.buffer,bytes.byteOffset,bytes.byteLength);
 if(b.length<24||b.length>5*1024*1024)return invalid();
 let width=0,height=0;let mime:ProfileImageInfo['mime'];
 if(declared==='image/png'){
  if(!b.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))||b.readUInt32BE(8)!==13||b.toString('ascii',12,16)!=='IHDR')return invalid();
  width=b.readUInt32BE(16);height=b.readUInt32BE(20);
  if(b.length<33||![0,2,3,4,6].includes(b[25])||![1,2,4,8,16].includes(b[24])||b[26]!==0||b[27]!==0||b[28]>1)return invalid();
  mime='image/png';
 }else if(declared==='image/jpeg'){
  if(b[0]!==0xff||b[1]!==0xd8||b[2]!==0xff)return invalid();
  mime='image/jpeg';let offset=2;let found=false;
  while(offset+4<=b.length){
   if(b[offset]!==0xff)return invalid();
   while(offset<b.length&&b[offset]===0xff)offset++;
   if(offset>=b.length)return invalid();
   const marker=b[offset++];
   if(marker===0xd9||marker===0xda)break;
   if(marker===0x00||marker===0x01||marker>=0xd0&&marker<=0xd7)return invalid();
   if(offset+2>b.length)return invalid();
   const size=b.readUInt16BE(offset);
   if(size<2||offset+size>b.length)return invalid();
   if([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(marker)){
    if(size<8)return invalid();
    height=b.readUInt16BE(offset+3);width=b.readUInt16BE(offset+5);found=true;break;
   }
   offset+=size;
  }
  if(!found)return invalid();
 }else if(declared==='image/webp'){
  if(b.length<30||b.toString('ascii',0,4)!=='RIFF'||b.toString('ascii',8,12)!=='WEBP'||b.readUInt32LE(4)!==b.length-8)return invalid();
  const chunk=b.toString('ascii',12,16);const length=b.readUInt32LE(16);
  if(length<5||20+length>b.length)return invalid();
  if(chunk==='VP8X'){
   if(length<10)return invalid();
   width=1+b.readUIntLE(24,3);height=1+b.readUIntLE(27,3);
  }else if(chunk==='VP8L'){
   if(b[20]!==0x2f)return invalid();
   width=1+(((b[22]&0x3f)<<8)|b[21]);height=1+(((b[24]&0x0f)<<10)|(b[23]<<2)|(b[22]>>6));
  }else if(chunk==='VP8 '){
   if(length<10||b[23]!==0x9d||b[24]!==0x01||b[25]!==0x2a)return invalid();
   width=b.readUInt16LE(26)&0x3fff;height=b.readUInt16LE(28)&0x3fff;
  }else return invalid();
  mime='image/webp';
 }else return invalid();
 if(!validDimensions(width,height))return invalid();
 return {mime,width,height};
}
