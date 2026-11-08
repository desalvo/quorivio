/** Bounded-memory S3 multipart PUT with AWS Signature V4; no SDK or runtime
 * network dependency. All endpoints require TLS, redirect following disabled. */
import {createHash,createHmac} from 'node:crypto';
import {open,stat} from 'node:fs/promises';
import type {BackupTarget} from './backup-storage.js';
const sha=(data:Buffer|string)=>createHash('sha256').update(data).digest('hex');
function hmac(key:Buffer|string,value:string):Buffer{return createHmac('sha256',key).update(value).digest()}
function xml(v:string):string{return v.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;')}
function decodeXml(v:string){return v.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&apos;/g,"'")}
function s3Root(target:BackupTarget){
 const endpoint=target.endpoint||`https://s3.${target.region}.amazonaws.com`;
 const url=new URL(endpoint);if(url.protocol!=='https:'||url.username||url.password||url.search||url.hash)throw Error('invalid_s3_endpoint');
 return `${endpoint.replace(/\/$/,'')}/${encodeURIComponent(target.bucket!)}`;
}
/** Exported for deterministic test fixtures. */
export function signS3Request(args:{method:string;url:string;region:string;accessKey:string;secretKey:string;payload:Buffer;date:Date;token?:string}){
 const u=new URL(args.url),amzDate=args.date.toISOString().replace(/[:-]|\.\d{3}/g,''),shortDate=amzDate.slice(0,8);
 const query=[...u.searchParams.entries()].map(([k,v])=>[encodeURIComponent(k),encodeURIComponent(v)] as const).sort(([a,av],[b,bv])=>a.localeCompare(b)||av.localeCompare(bv)).map(([k,v])=>`${k}=${v}`).join('&');
 const hash=sha(args.payload);
 const headers:Record<string,string>={host:u.host,'x-amz-content-sha256':hash,'x-amz-date':amzDate};
 if(args.token)headers['x-amz-security-token']=args.token;
 const keys=Object.keys(headers).sort(),canonicalHeaders=keys.map(k=>`${k}:${headers[k]}\n`).join(''),signedHeaders=keys.join(';');
 const canonical=[args.method,u.pathname,query,canonicalHeaders,signedHeaders,hash].join('\n');
 const scope=`${shortDate}/${args.region}/s3/aws4_request`;
 const stringToSign=`AWS4-HMAC-SHA256\n${amzDate}\n${scope}\n${sha(canonical)}`;
 const signing=hmac(hmac(hmac(hmac(`AWS4${args.secretKey}`,shortDate),args.region),'s3'),'aws4_request');
 const signature=createHmac('sha256',signing).update(stringToSign).digest('hex');
 return {'x-amz-content-sha256':hash,'x-amz-date':amzDate,...(args.token?{'x-amz-security-token':args.token}:{}),Authorization:`AWS4-HMAC-SHA256 Credential=${args.accessKey}/${scope}, SignedHeaders=${signedHeaders}, Signature=${signature}`};
}
async function s3Fetch(target:BackupTarget,method:string,url:string,data:Buffer){
 const accessKey=target.accessKey||process.env.AWS_ACCESS_KEY_ID||'',secretKey=target.secretKey||process.env.AWS_SECRET_ACCESS_KEY||'';
 if(!accessKey||!secretKey)throw Error('s3_credentials_required');
 const headers=signS3Request({method,url,region:target.region||'us-east-1',accessKey,secretKey,payload:data,date:new Date(),token:process.env.AWS_SESSION_TOKEN});
 const response=await fetch(url,{method,headers,body:method==='PUT'||method==='POST'?data:undefined,redirect:'manual',signal:AbortSignal.timeout(120000)});
 if(!response.ok)throw Error('s3_request_failed_'+response.status);
 return response;
}
export async function multipartS3Backup(target:BackupTarget,file:{archive:string;name:string}){
 const key=[target.prefix,file.name].filter(Boolean).join('/').split('/').map(encodeURIComponent).join('/');
 const base=s3Root(target)+'/'+key,body=new Uint8Array(0);
 const init=await s3Fetch(target,'POST',base+'?uploads=',Buffer.from(body));
 const xmlText=await init.text(),uploadId=decodeXml(xmlText.match(/<UploadId>([^<]+)<\/UploadId>/)?.[1]||'');
 if(!uploadId)throw Error('s3_upload_id_missing');
 const uploadQuery=`uploadId=${encodeURIComponent(uploadId)}`;
 const parts:{part:number;etag:string}[]=[];
 const fd=await open(file.archive,'r');
 try{
  const size=(await stat(file.archive)).size,chunkSize=8*1024*1024;
  if(Math.ceil(size/chunkSize)>10000)throw Error('s3_too_many_parts');
  for(let pos=0,part=1;pos<size;pos+=chunkSize,part++){
   const buffer=Buffer.allocUnsafe(Math.min(chunkSize,size-pos));
   let offset=0;while(offset<buffer.length){const n=await fd.read(buffer,offset,buffer.length-offset,pos+offset);if(n.bytesRead===0)throw Error('backup_file_truncated');offset+=n.bytesRead}
   const reply=await s3Fetch(target,'PUT',base+`?partNumber=${part}&${uploadQuery}`,buffer);
   const etag=reply.headers.get('etag');if(!etag)throw Error('s3_etag_missing');
   parts.push({part,etag});
  }
  const complete=Buffer.from(`<CompleteMultipartUpload>${parts.map(({part,etag})=>`<Part><PartNumber>${part}</PartNumber><ETag>${xml(etag)}</ETag></Part>`).join('')}</CompleteMultipartUpload>`);
  const finished=await s3Fetch(target,'POST',base+'?'+uploadQuery,complete);
  if((await finished.text()).includes('<Error>'))throw Error('s3_complete_failed');
 }catch(e){await s3Fetch(target,'DELETE',base+'?'+uploadQuery,Buffer.from(body)).catch(()=>{});throw e}
 finally{await fd.close()}
}
