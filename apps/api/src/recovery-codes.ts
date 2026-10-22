import {randomBytes,createHmac} from 'node:crypto';
/** One-time recovery tokens: 128 bits, grouped for transcription. Never log raw tokens. */
export function generateRecoveryCodes(count=10){if(!Number.isInteger(count)||count<1||count>20)throw new Error('invalid count');return Array.from({length:count},()=>randomBytes(16).toString('hex').toUpperCase().match(/.{1,8}/g)!.join('-'));}
export function validRecoveryCode(value:unknown):value is string{return typeof value==='string'&&/^[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{8}){3}$/.test(value)}
export function recoveryCodeDigest(code:string,key:string){return createHmac('sha256',key).update('quorivio-mfa-recovery-v1:'+code.replace(/-/g,'').toUpperCase()).digest('hex')}
