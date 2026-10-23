import {createHmac, randomInt, timingSafeEqual} from 'node:crypto';

/** Stateless primitives used by the database-backed email MFA flow.
 * OTPs are not access tokens; the challenge is consumed transactionally before issuing a session.
 */
export function createEmailOtp():string {return randomInt(0,1_000_000).toString().padStart(6,'0')}
export function validEmailOtp(value:unknown):value is string{return typeof value==='string'&&/^\d{6}$/.test(value)}
export function emailOtpDigest(code:string, userId:string, challengeId:string, secret:string):string{
 if(!validEmailOtp(code)||!userId||!challengeId||secret.length<32)throw Error('invalid_email_otp_digest_input');
 return createHmac('sha256',secret).update('quorivio-email-otp-v1\0').update(userId).update('\0').update(challengeId).update('\0').update(code).digest('hex');
}
export function matchesEmailOtp(code:unknown, expectedDigest:string, userId:string, challengeId:string, secret:string):boolean{
 if(!validEmailOtp(code)||!/^[a-f0-9]{64}$/.test(expectedDigest))return false;
 const actual=Buffer.from(emailOtpDigest(code,userId,challengeId,secret),'hex');
 return timingSafeEqual(actual,Buffer.from(expectedDigest,'hex'));
}
