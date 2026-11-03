/** Explicitly opted-in Gravatar import. No user-supplied URLs or outbound
 * requests for people who have not enabled the integration. */
import {createHash} from 'node:crypto';
export const GRAVATAR_MAX_BYTES=5*1024*1024;
export function gravatarHash(email:string):string{
 return createHash('sha256').update(email.trim().toLowerCase(),'utf8').digest('hex');
}
export function gravatarAvatarUrl(email:string):string{
 return `https://gravatar.com/avatar/${gravatarHash(email)}?d=404&s=256&r=g`;
}
export type GravatarResult={status:'missing'}|{status:'found';data:Buffer;mime:'image/png'|'image/jpeg'|'image/webp';sha256:string};
export async function downloadGravatar(email:string,request:typeof fetch=fetch):Promise<GravatarResult>{
 const response=await request(gravatarAvatarUrl(email),{
  method:'GET',redirect:'manual',signal:AbortSignal.timeout(4500),
  headers:{'Accept':'image/png,image/jpeg,image/webp','User-Agent':'Quorivio-Gravatar/1.0'}
 });
 if(response.status===404)return {status:'missing'};
 if(response.status!==200||!response.body)throw Error('gravatar_unavailable');
 const contentType=response.headers.get('content-type')?.split(';')[0]?.trim().toLowerCase();
 if(contentType!=='image/png'&&contentType!=='image/jpeg'&&contentType!=='image/webp'){
  await response.body.cancel();throw Error('gravatar_invalid_media');
 }
 const declared=Number(response.headers.get('content-length')||'0');
 if(declared>GRAVATAR_MAX_BYTES){await response.body.cancel();throw Error('gravatar_oversized');}
 const reader=response.body.getReader();const parts:Uint8Array[]=[];let total=0;
 try{
  while(true){const {value,done}=await reader.read();if(done)break;
   if(value){total+=value.length;if(total>GRAVATAR_MAX_BYTES)throw Error('gravatar_oversized');parts.push(value)}
  }
 }finally{await reader.cancel().catch(()=>{});}
 if(total<24)throw Error('gravatar_invalid_media');
 const data=Buffer.concat(parts,total);
 return {status:'found',data,mime:contentType,sha256:createHash('sha256').update(data).digest('hex')};
}
