/** Validate all requested platform settings before starting a database transaction.
 * Reject partial updates rather than persisting the first valid field and then failing. */
export type SettingsPatch={public_base_url?:string;closed_session_retention_days?:number;max_upload_mb?:number};
export type SettingsPatchResult={ok:true;changes:[string,string][]}|{ok:false;error:string};
export function validateSettingsPatch(input:unknown):SettingsPatchResult{
 if(!input||typeof input!=='object'||Array.isArray(input))return {ok:false,error:'invalid_update'};
 const value=input as Record<string,unknown>;
 const changes:[string,string][]=[];
 if(value.public_base_url!==undefined){
  if(typeof value.public_base_url!=='string'||value.public_base_url.length>2048||!/^https:\/\/[^\s/?#]+$/.test(value.public_base_url))return {ok:false,error:'invalid_public_url'};
  try{
   const url=new URL(value.public_base_url);
   if(url.protocol!=='https:'||!url.hostname||url.username||url.password||url.pathname!=='/'||url.search||url.hash)return {ok:false,error:'invalid_public_url'};
  }catch{return {ok:false,error:'invalid_public_url'}}
  changes.push(['public_base_url',value.public_base_url]);
 }
 if(value.closed_session_retention_days!==undefined){
  if(typeof value.closed_session_retention_days!=='number'||!Number.isInteger(value.closed_session_retention_days)||value.closed_session_retention_days<1||value.closed_session_retention_days>3650)return {ok:false,error:'invalid_retention'};
  changes.push(['closed_session_retention_days',String(value.closed_session_retention_days)]);
 }
 if(value.max_upload_mb!==undefined){
  if(typeof value.max_upload_mb!=='number'||!Number.isInteger(value.max_upload_mb)||value.max_upload_mb<1||value.max_upload_mb>1024)return {ok:false,error:'invalid_upload_limit'};
  changes.push(['max_upload_mb',String(value.max_upload_mb)]);
 }
 return {ok:true,changes};
}
