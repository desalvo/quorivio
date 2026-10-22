import {randomBytes,createHash,createCipheriv,createDecipheriv} from 'node:crypto';
import {smtpConfigFromEnv,type SmtpConfig} from './smtp.js';
export function validateSmtpInput(input:any):SmtpConfig{
 const obj={SMTP_HOST:input?.host,SMTP_PORT:String(input?.port??465),SMTP_SECURE:input?.secure===false?'false':'true',SMTP_USER:input?.user,SMTP_PASSWORD:input?.password,SMTP_FROM:input?.from,SMTP_SENDER_NAME:input?.senderName??''};
 const c=smtpConfigFromEnv(obj as NodeJS.ProcessEnv);if(!c||c.password.length<1)throw Error('invalid_smtps_configuration');return c;
}
function cryptoKey(secret:string){return createHash('sha256').update('quorivio-smtp-config-v1:').update(secret).digest()}
export function sealSmtpConfig(config:SmtpConfig,secret:string){const iv=randomBytes(12),cipher=createCipheriv('aes-256-gcm',cryptoKey(secret),iv);const data=Buffer.concat([cipher.update(JSON.stringify(config),'utf8'),cipher.final()]);return ['v1',iv.toString('base64url'),cipher.getAuthTag().toString('base64url'),data.toString('base64url')].join('.')}
export function openSmtpConfig(blob:string,secret:string):SmtpConfig{const [version,iv,tag,data,...more]=blob.split('.');if(version!=='v1'||!iv||!tag||!data||more.length)throw Error('invalid_smtp_blob');const decipher=createDecipheriv('aes-256-gcm',cryptoKey(secret),Buffer.from(iv,'base64url'));decipher.setAuthTag(Buffer.from(tag,'base64url'));const parsed=JSON.parse(Buffer.concat([decipher.update(Buffer.from(data,'base64url')),decipher.final()]).toString('utf8'));return validateSmtpInput(parsed)}
export function publicSmtpConfig(c:SmtpConfig|null){return {configured:!!c,transport:c?(c.secure?'smtps':'starttls'):null,host:c?.host??null,port:c?.port??null,from:c?.from??null,senderName:c?.senderName??'',user:c?.user??null,password_configured:!!c?.password}}
