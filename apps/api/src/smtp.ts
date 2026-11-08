/** Environment-only SMTP credentials: never persist passwords or return them to the UI. */
export type SmtpConfig={host:string;port:number;secure:boolean;user:string;password:string;from:string;senderName?:string};
export function smtpConfigFromEnv(env:NodeJS.ProcessEnv):SmtpConfig|null{
 const host=env.SMTP_HOST||'',port=Number(env.SMTP_PORT||465),secure=env.SMTP_SECURE!=='false',user=env.SMTP_USER||'',password=env.SMTP_PASSWORD||'',from=env.SMTP_FROM||'',senderName=env.SMTP_SENDER_NAME||'';
 if(!host&&!user&&!password&&!from)return null;
 if(!/^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$/.test(host)||!Number.isInteger(port)||port<1||port>65535||!user||!password||!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(from))throw new Error('invalid SMTP configuration');
 if(senderName.length>120||/[\r\n]/.test(senderName))throw new Error('invalid SMTP sender name');
 return {host,port,secure,user,password,from,senderName};
}
export function smtpPublicSettings(env:NodeJS.ProcessEnv){try{const c=smtpConfigFromEnv(env);return {configured:!!c,transport:c?'smtps':null,host:c?.host||null,port:c?.port||null,from:c?.from||null}}catch{return {configured:false,error:'invalid_smtp_configuration'}}}
export async function sendPasswordResetEmail(c:SmtpConfig,to:string,link:string){
 const {default:mailer}=await import('nodemailer');
 const transport=mailer.createTransport({host:c.host,port:c.port,secure:c.secure,requireTLS:!c.secure,auth:{user:c.user,pass:c.password},connectionTimeout:10000,greetingTimeout:10000,socketTimeout:15000,tls:{rejectUnauthorized:true}});
 try{await transport.sendMail({from:c.senderName?{name:c.senderName,address:c.from}:c.from,to,subject:'Quorivio - Password recovery',text:`To reset your Quorivio password, open the following link within 20 minutes:\n\n${link}\n\nIf you did not request this, ignore this email. Your MFA authenticator remains enabled.`})}finally{transport.close()}
}
export async function sendTestEmail(c:SmtpConfig,to:string){
 // nodemailer automatically validates the server certificate and supports SMTP AUTH.
 const {default:mailer}=await import('nodemailer');
 const transport=mailer.createTransport({host:c.host,port:c.port,secure:c.secure,requireTLS:!c.secure,auth:{user:c.user,pass:c.password},connectionTimeout:10000,greetingTimeout:10000,socketTimeout:15000,tls:{rejectUnauthorized:true}});
 try{await transport.sendMail({from:c.senderName?{name:c.senderName,address:c.from}:c.from,to,subject:'Quorivio SMTP connection test',text:'This is a test email from your Quorivio installation.'})}finally{transport.close()}
}

/** Transport for optional email second-factor challenges; activation requires a
 * database-backed single-use challenge flow and configured SMTP. */
export async function sendEmailOtp(c:SmtpConfig,to:string,code:string,validMinutes=5){
 if(!/^\d{6}$/.test(code)||!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(to)||!Number.isInteger(validMinutes)||validMinutes<1||validMinutes>15)throw Error('invalid_email_otp_delivery');
 const {default:mailer}=await import('nodemailer');
 const transport=mailer.createTransport({host:c.host,port:c.port,secure:c.secure,requireTLS:!c.secure,auth:{user:c.user,pass:c.password},connectionTimeout:10000,greetingTimeout:10000,socketTimeout:15000,tls:{rejectUnauthorized:true}});
 try{await transport.sendMail({from:c.senderName?{name:c.senderName,address:c.from}:c.from,to,subject:'Quorivio - Verification code',text:`Your Quorivio verification code is ${code}. It expires in ${validMinutes} minutes. If you did not request this code, ignore this message.`})}finally{transport.close()}
}

/** Platform-wide disk capacity warning. Only backend-selected platform admins
 * receive this message; request inputs never control recipients or content. */
export async function sendDiskCapacityAlert(c:SmtpConfig,recipients:string[],volume:'application'|'conversion'|'database',percent:number,usedBytes:number,totalBytes:number){
 if(!recipients.length||!Number.isFinite(percent)||percent<90||percent>100||!Number.isSafeInteger(usedBytes)||!Number.isSafeInteger(totalBytes)||usedBytes>totalBytes||usedBytes<0)throw Error('invalid_disk_alert');
 const safe=recipients.filter(r=>/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(r));
 if(safe.length!==recipients.length)throw Error('invalid_disk_alert_recipient');
 const {default:mailer}=await import('nodemailer');
 const transport=mailer.createTransport({host:c.host,port:c.port,secure:c.secure,requireTLS:!c.secure,auth:{user:c.user,pass:c.password},connectionTimeout:10000,greetingTimeout:10000,socketTimeout:15000,tls:{rejectUnauthorized:true}});
 const label=volume==='database'?'PostgreSQL data volume':volume==='conversion'?'Quorivio conversion temporary volume':'Quorivio application asset volume';
 const gib=(bytes:number)=>(bytes/1073741824).toFixed(2);
 try{const delivery=await transport.sendMail({from:c.senderName?{name:c.senderName,address:c.from}:c.from,to:safe,subject:`[Quorivio] DISK SPACE ALERT: ${label} at ${percent.toFixed(1)}%`,text:`Quorivio detected that ${label} is ${percent.toFixed(1)}% full (threshold: 90%).\nUsed: ${gib(usedBytes)} GiB of ${gib(totalBytes)} GiB.\n\nPlease check free disk space and storage provisioning promptly. The warning is re-armed after utilization falls to 85% or below.\n`});if(delivery.rejected?.length||!delivery.accepted?.length)throw Error('disk_alert_delivery_not_accepted')}finally{transport.close()}
}

/** Registration requests are sent to all approved platform administrators. */
export async function sendRegistrationReviewEmail(c:SmtpConfig,recipients:string[],email:string,backend:'local'|'ldap'){
 if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)||!recipients.length)return;
 const {default:mailer}=await import('nodemailer');
 const transport=mailer.createTransport({host:c.host,port:c.port,secure:c.secure,requireTLS:!c.secure,auth:{user:c.user,pass:c.password},tls:{rejectUnauthorized:true},connectionTimeout:10000,socketTimeout:15000});
 try{await transport.sendMail({from:c.senderName?{name:c.senderName,address:c.from}:c.from,to:recipients,subject:'[Quorivio] Nuova richiesta di registrazione',text:`L'utente ${email} ha richiesto accesso con backend ${backend.toUpperCase()}. L'account resta disabilitato finché un amministratore non lo approva nella sezione Utenti.`})}finally{transport.close()}
}
