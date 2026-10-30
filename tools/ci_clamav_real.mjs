/** Real clamd INSTREAM regression for the disposable opt-in GitHub Actions job.
 * The harmless EICAR industry-standard test pattern is constructed at runtime.
 * Diagnostics intentionally contain only fixed stage/reason identifiers: never
 * raw clamd replies, user file contents, paths or scanner internals.
 */
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {connect} from 'node:net';
import {scanUploadedFile} from '../apps/api/src/malware-scan.ts';

const host='127.0.0.1';
const port=23310;
const env={CLAMAV_HOST:host,CLAMAV_PORT:String(port),CLAMAV_TIMEOUT_MS:'120000',
  NODE_ENV:'production',QUORIVIO_AV_REQUIRED:'true'};
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));

// TCP connect alone does not establish that clamd has loaded its signature
// databases. Only the official PING/PONG command proves daemon readiness.
export async function pingClamd(hostname=host,portNumber=port,timeoutMs=3000){
 return new Promise(resolve=>{
  let done=false,received='';
  const socket=connect({host:hostname,port:portNumber});
  const finish=ready=>{if(done)return;done=true;clearTimeout(timer);socket.destroy();resolve(ready)};
  const timer=setTimeout(()=>finish(false),timeoutMs);
  socket.on('connect',()=>socket.write(Buffer.from('zPING\0')));
  socket.on('data',chunk=>{
   received+=chunk.toString('utf8');
   if(received.length>32){finish(false);return}
   const terminator=received.indexOf('\0');
   if(terminator>=0)finish(received.slice(0,terminator)==='PONG' &&
     received.slice(terminator+1).length===0);
  });
  socket.on('error',()=>finish(false));
  socket.on('end',()=>finish(false));
  socket.on('close',()=>finish(false));
 });
}

export async function waitUntilClamdReady(probe=pingClamd,{
 timeoutMs=300000,intervalMs=2000,now=()=>Date.now(),sleep=delay
}={}){
 const deadline=now()+timeoutMs;
 do{
  if(await probe())return true;
  if(now()>=deadline)return false;
  await sleep(Math.min(intervalMs,Math.max(1,deadline-now())));
 }while(true);
}

function safeReason(error){
 // Return ONLY preapproved error classes; never reflect raw daemon responses.
 const allowed=new Set(['malware_detected','antivirus_scan_failed',
  'antivirus_connection_error','antivirus_connection_closed',
  'antivirus_timeout','antivirus_premature_response',
  'antivirus_invalid_response','antivirus_response_too_large',
  'antivirus_file_changed','invalid_antivirus_input_size']);
 return error instanceof Error && allowed.has(error.message)
   ?error.message:'unexpected_failure';
}

export async function realClamdAcceptance(scan=scanUploadedFile,ready=waitUntilClamdReady){
 if(!await ready())throw Error('clamd_not_ready');
 const folder=await mkdtemp(join(tmpdir(),'quorivio-clamd-ci-'));
 try{
  const clean=join(folder,'clean-file');
  const eicar=join(folder,'av-detection-test');
  await writeFile(clean,Buffer.from('Quorivio disposable clean antivirus test file.'));
  // The 68-byte harmless EICAR pattern is never checked into the repository.
  const signature=['X5O!P%@AP[4\\PZX54(P^)7CC)7}',
                   '$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'].join('');
  if(Buffer.byteLength(signature,'ascii')!==68)throw Error('invalid_test_pattern');
  await writeFile(eicar,Buffer.from(signature,'ascii'));
  try{await scan(clean,env)}
  catch(error){throw Error('clean_scan_'+safeReason(error))}
  let blocked=false;
  try{await scan(eicar,env)}
  catch(error){
   if(error instanceof Error && error.message==='malware_detected')blocked=true;
   else throw Error('eicar_scan_'+safeReason(error));
  }
  if(!blocked)throw Error('eicar_not_detected');
  return 'PASS real clamd: clean file accepted; EICAR test pattern blocked (CI only)';
 }finally{await rm(folder,{recursive:true,force:true})}
}

if(process.argv[1] && fileURLToPath(import.meta.url)===resolve(process.argv[1])){
 const readyOnly=process.argv.includes('--wait-ready');
 (async()=>{
  if(readyOnly){
   if(!await waitUntilClamdReady())throw Error('clamd_not_ready');
   console.log('PASS clamd PING/PONG readiness (CI only)');
  }else console.log(await realClamdAcceptance());
 })().catch(error=>{
  const stage=error instanceof Error && /^(clamd_not_ready|invalid_test_pattern|clean_scan_[a-z_]+|eicar_scan_[a-z_]+|eicar_not_detected)$/.test(error.message)
   ?error.message:'unexpected_failure';
  console.error('FAIL real ClamAV acceptance stage='+stage+' (details redacted)');
  process.exitCode=1;
 });
}
