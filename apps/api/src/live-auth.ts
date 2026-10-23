/** Session revocation shared by HTTP and live presenter connections. */
export function authCookieIssuedAt(cookie:string|undefined,ttlMs=8*3600*1000):number|null{
 const match=/(?:^|;\s*)q_auth=([^;]+)/.exec(cookie||'');
 const expiry=match?.[1]?.split('.')[1];
 if(!expiry||!/^\d+$/.test(expiry))return null;
 const issued=Number(expiry)-ttlMs;
 return Number.isSafeInteger(issued)&&issued>0?issued:null;
}
export function presenterAuthActive(account:{approved:boolean;must_change_password:boolean;auth_revoked_at:Date|string|null;password_changed_at:Date|string|null}|undefined,issued:number|null){
 if(!account||!account.approved||account.must_change_password||issued===null)return false;
 return [account.auth_revoked_at,account.password_changed_at].every(v=>!v||issued>=new Date(v).getTime());
}
