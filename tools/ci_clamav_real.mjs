/** Real clamd INSTREAM regression. Only called inside disposable opt-in CI.
 * EICAR is a harmless industry-standard antivirus test string, assembled at
 * runtime so no test signature is shipped in the source/archive.
 */
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {scanUploadedFile} from '../apps/api/src/malware-scan.ts';

const host='127.0.0.1';
const port=23310;
const env={CLAMAV_HOST:host,CLAMAV_PORT:String(port),CLAMAV_TIMEOUT_MS:'120000',
  NODE_ENV:'production',QUORIVIO_AV_REQUIRED:'true'};
async function test(){
 const folder=await mkdtemp(join(tmpdir(),'quorivio-clamd-ci-'));
 try{
  const clean=join(folder,'clean-file');
  const eicar=join(folder,'av-detection-test');
  await writeFile(clean,Buffer.from('Quorivio disposable clean antivirus test file.'));
  // The encoded pieces are concatenated only in the isolated runner. This is
  // the EICAR test pattern, not malicious executable code or real malware.
  const signature=['X5O!P%@AP[4\\PZX54(P^)7CC)7}',
                   '$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'].join('');
  await writeFile(eicar,Buffer.from(signature,'ascii'));
  await scanUploadedFile(clean,env);
  let detected=false;
  try{await scanUploadedFile(eicar,env)}
  catch(err){if(err instanceof Error && err.message==='malware_detected')detected=true;else throw Error('unexpected_scanner_failure')}
  if(!detected)throw Error('actual_antivirus_signature_not_detected');
  console.log('PASS real clamd: clean file accepted; EICAR test signature blocked in production mode (CI only)');
 }finally{await rm(folder,{recursive:true,force:true})}
}
test().catch(()=>{console.error('FAIL real ClamAV signature acceptance (details redacted)');process.exitCode=1});
