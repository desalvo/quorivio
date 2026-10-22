/** Strict allowlist for binary session assets. Never trust the declared Content-Type alone. */
export const ACCEPTED_TYPES = ['image/png','image/jpeg','image/gif','image/webp','application/pdf','video/mp4','video/webm'] as const;
export function sniffAsset(data:Buffer):string|null {
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
export function validAsset(data:Buffer,declared:string,maximumBytes:number){return data.length>0&&data.length<=maximumBytes&&sniffAsset(data)===declared&&ACCEPTED_TYPES.includes(declared as any)}
