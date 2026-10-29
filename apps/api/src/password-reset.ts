import {createHash,randomBytes} from 'node:crypto';
export const RESET_TTL_MINUTES=20;
export function normalizeResetEmail(value:unknown):string|null {if(typeof value!=='string')return null;const email=value.trim().toLowerCase();return email.length<=254&&/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)?email:null}
export function generateResetToken(){return randomBytes(32).toString('base64url')}
export function resetTokenDigest(token:string){return createHash('sha256').update(token).digest('hex')}
export function validResetToken(token:unknown):token is string{return typeof token==='string'&&/^[A-Za-z0-9_-]{43}$/.test(token)}
export function validNewPassword(password:unknown):password is string{return typeof password==='string'&&password.length>=12&&password.length<=256}
/** Never transmit a recovery bearer in the HTTP request line or the Referer.
 * URL fragments are not sent to the web server. The browser consumes the
 * fragment before application navigation; old query-format links remain
 * supported by consumeRecoveryTokenFromUrl for existing emailed links.
 */
export function resetLink(base:string,token:string){
  const u=new URL(base);
  u.pathname='/';
  u.search='';
  u.hash=new URLSearchParams({reset_token:token}).toString();
  return u.toString();
}
