/** Upload error policy for the private presenter background endpoint.
 * Only stable error codes cross the API. Kubernetes logs disclose the phase
 * and a known error category, never filenames, owners, paths, or raw SQL.
 */
export type BackgroundUploadPhase='authorization'|'receiving'|'scanning'|'registering'|'applying';
export type BackgroundUploadFailure={status:number;code:string;category:string};

export function classifyBackgroundUploadFailure(phase:BackgroundUploadPhase,error:unknown):BackgroundUploadFailure{
 const value=error&&typeof error==='object'?error as {code?:unknown;message?:unknown}:{};
 const code=typeof value.code==='string'?value.code:'';
 const message=typeof value.message==='string'?value.message:'';
 if(message==='invalid_upload_size'||message==='upload_too_large')return {status:413,code:'invalid_upload_size',category:'invalid_size'};
 if(message==='upload_length_mismatch')return {status:400,code:'upload_length_mismatch',category:'incomplete_body'};
 if(message==='invalid_media_signature')return {status:415,code:'invalid_media_signature',category:'signature_mismatch'};
 if(message==='malware_detected')return {status:422,code:'malware_detected',category:'infected_file'};
 // Keep the scanner fail-closed. TCP readiness alone is not proof that clamd
 // has loaded its databases or can accept an entire INSTREAM request.
 if(phase==='scanning'||message.startsWith('antivirus_')||message==='invalid_antivirus_input_file')
  return {status:503,code:'antivirus_unavailable',category:/timeout/.test(message)?'scanner_timeout':'scanner_unavailable'};
 // NFS/CephFS/PVC volumes mounted read-only or with a mismatched UID/GID
 // need operational remediation: never chmod the mount or bypass AV here.
 if(['EACCES','EPERM','EROFS'].includes(code))return {status:507,code:'background_storage_unavailable',category:'volume_permissions'};
 if(['ENOSPC','EDQUOT'].includes(code))return {status:507,code:'background_storage_unavailable',category:'volume_capacity'};
 if(['EIO','ESTALE'].includes(code))return {status:503,code:'background_storage_unavailable',category:'volume_io'};
 // PostgreSQL uses a five-character SQLSTATE. Do not disclose SQL or values.
 if(/^[0-9A-Z]{5}$/.test(code))return {status:503,code:'background_database_unavailable',category:'database_error'};
 if(phase==='registering')return {status:503,code:'background_database_unavailable',category:'database_error'};
 return {status:500,code:'background_processing_failed',category:'internal_error'};
}

/** A log-safe fingerprint: neither error.message nor user identifiers are logged. */
export function backgroundUploadLog(phase:BackgroundUploadPhase,error:unknown){
 const result=classifyBackgroundUploadFailure(phase,error);
 return JSON.stringify({phase,category:result.category,status:result.status});
}
