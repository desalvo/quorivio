/** Privacy-by-design audit: no request bodies, credentials, IPs, cookies or full URLs. */
export const AUDIT_ALLOWED_ROUTES = /^\/api\/(?:admin\/|sessions\/|presenters\/|auth\/mfa\/)/;
export function auditOperation(method:string,route:string,status:number){
 if(!['POST','PATCH','PUT','DELETE'].includes(method)||status<200||status>=400||!AUDIT_ALLOWED_ROUTES.test(route))return null;
 // The server passes only the matched route template, not unsanitized path input.
 const sanitized=route.replace(/[0-9a-f]{8}-[0-9a-f-]{27,}/ig,':id').slice(0,180);
 return {action:method.toLowerCase(),resource_type:sanitized};
}
export function validAuditRetention(days:unknown):days is number{return Number.isSafeInteger(days)&&Number(days)>=7&&Number(days)<=3650}
