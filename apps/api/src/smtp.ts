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
